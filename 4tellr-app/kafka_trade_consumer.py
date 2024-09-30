import os
import uuid
import json
import logging
import signal
import requests
from datetime import datetime
from configparser import ConfigParser
from typing import Dict, Any, List, Tuple
from jsonschema import validate
import time
import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import ConsumerStoppedError
from prometheus_client import Counter, Histogram, CollectorRegistry, push_to_gateway
from helpers.mongodb_helper import MongoDBHelper
from services.event_services import EventServices
from logging.handlers import RotatingFileHandler
import concurrent.futures

# Prometheus metrics setup
REGISTRY = CollectorRegistry()
MESSAGE_COUNTER = Counter('kafka_messages_processed', 'Number of Kafka messages processed', registry=REGISTRY)
MESSAGE_LATENCY = Histogram('kafka_message_latency_seconds', 'Message processing latency in seconds', registry=REGISTRY)
DLQ_COUNTER = Counter('dlq_messages', 'Number of messages sent to dead-letter queue', registry=REGISTRY)

class ConfigLoader:
    def __init__(self, logger):
        self.logger = logger
        self.config = self._load_config()

    def _load_config(self):
        config_parser = ConfigParser()
        config_parser.read('config.txt')

        return {
            'MONGO_URI': os.getenv('MONGO_URI', config_parser.get('DEFAULT', 'MONGO_URI')),
            'KAFKA_BOOTSTRAP_SERVERS': os.getenv('KAFKA_BOOTSTRAP_SERVERS', config_parser.get('KAFKA', 'BOOTSTRAP_SERVERS')),
            'KAFKA_TOPIC': os.getenv('KAFKA_TOPIC', config_parser.get('KAFKA', 'TOPIC')),
            'KAFKA_GROUP_ID': os.getenv('KAFKA_GROUP_ID', config_parser.get('KAFKA', 'GROUP_ID')),
            'PROMETHEUS_PUSHGATEWAY': os.getenv('PROMETHEUS_PUSHGATEWAY', 'localhost:9091'),
            'KAFKA_DLQ_TOPIC': 'trade_events_errors',
        }

    def get(self, key):
        return self.config.get(key)

class Metrics:
    def __init__(self, config: ConfigLoader, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.prometheus_available = False
        self.check_prometheus_connection()

    def check_prometheus_connection(self):
        pushgateway_url = f"http://{self.config.get('PROMETHEUS_PUSHGATEWAY')}"
        max_retries = 2
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                response = requests.get(pushgateway_url, timeout=5)
                if response.status_code == 200:
                    self.prometheus_available = True
                    self.logger.info("Successfully connected to Prometheus Pushgateway")
                    return
            except requests.RequestException:
                self.logger.warning(f"Failed to connect to Prometheus Pushgateway (attempt {attempt + 1}/{max_retries})")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

        self.logger.warning("Unable to connect to Prometheus Pushgateway. Continuing without Prometheus metrics.")

    def record_metrics(self, num_messages: int, processing_time: float):
        if self.prometheus_available:
            MESSAGE_COUNTER.inc(num_messages)
            MESSAGE_LATENCY.observe(processing_time)
            try:
                push_to_gateway(self.config.get('PROMETHEUS_PUSHGATEWAY'), job='kafka_consumer', registry=REGISTRY)
            except Exception as e:
                self.logger.error(f"Failed to push metrics to Prometheus: {e}")

    def record_dlq_message(self):
        if self.prometheus_available:
            DLQ_COUNTER.inc()
            try:
                push_to_gateway(self.config.get('PROMETHEUS_PUSHGATEWAY'), job='kafka_consumer', registry=REGISTRY)
            except Exception as e:
                self.logger.error(f"Failed to push DLQ metric to Prometheus: {e}")


class EventProcessor:
    def __init__(self, event_services, logger):
        self.event_services = event_services
        self.logger = logger
        self.schema = self._load_schema()

    def _load_schema(self):
        return {
            "type": "object",
            "properties": {
                "process_id": {"type": "string"},
                "trade_id": {"type": "integer"},
                "status": {"type": "string"},
                "timestamp": {"type": "string"},
                "application": {"type": "string"}
            },
            "required": ["trade_id", "status", "timestamp"]
        }

    def validate_message(self, message: Dict[str, Any]) -> bool:
        try:
            validate(instance=message, schema=self.schema)
            return True
        except Exception:
            return False

    def transform_message(self, trade_event: Dict[str, Any]) -> Dict[str, Any]:
        trade_id = trade_event.get('trade_id', 'unknown')
        event_name = f"{trade_event.get('process_id', 'unknown')}-{trade_id}"

        return {
            'eventName': event_name,
            'tradeId': trade_id,
            'eventStatus': trade_event.get('status', 'unknown'),
            'businessDate': datetime.now().strftime('%Y-%m-%d'),
            'eventTime': trade_event.get('timestamp', 'unknown'),
            'eventType': 'MESSAGE',
            'batchOrRealtime': 'Realtime',
            'resource': 'trading app',
            'message': '',
            'details': {
                'messageId': trade_id,
                'messageQueue': 'trade_events',
                'application': trade_event.get('application', 'unknown')
            }
        }

    async def process_message(self, msg: Any, loop: asyncio.AbstractEventLoop) -> Tuple[bool, str]:
        try:
            trade_event = json.loads(msg.value.decode('utf-8'))
            if not self.validate_message(trade_event):
                error_info = "Invalid message format"
                self.logger.warning(f"{error_info}: {trade_event}")
                return False, error_info

            transformed_event = self.transform_message(trade_event)
            # Run synchronous insert_event in a thread pool
            await loop.run_in_executor(None, self.event_services.insert_event, transformed_event)
            self.logger.debug(f"Processed and inserted event: {transformed_event}")
            return True, ""
        except json.JSONDecodeError as e:
            error_info = f"JSON decode error: {str(e)}"
            self.logger.warning(f"{error_info}. Message: {msg.value}")
            return False, error_info
        except Exception as e:
            error_info = f"Unexpected error: {str(e)}"
            self.logger.error(f"{error_info}. Message: {msg.value}")
            return False, error_info

class KafkaTradeConsumer:
    def __init__(self, config: ConfigLoader, event_processor: EventProcessor, metrics: Metrics, logger: logging.Logger):
        self.config = config
        self.event_processor = event_processor
        self.metrics = metrics
        self.logger = logger
        self.consumer = None
        self.producer = None
        self.running = False
        self.start_time = None
        self.messages_processed = 0
        self.batch_size = 1000  # Process messages in batches
        self.empty_polls = 0
        self.max_empty_polls = 3  # Stop after this many consecutive empty polls

    async def setup_consumer(self):
        self.consumer = AIOKafkaConsumer(
            self.config.get('KAFKA_TOPIC'),
            bootstrap_servers=self.config.get('KAFKA_BOOTSTRAP_SERVERS'),
            group_id=f"{self.config.get('KAFKA_GROUP_ID')}-{uuid.uuid4()}",
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.config.get('KAFKA_BOOTSTRAP_SERVERS')
        )
        await self.consumer.start()
        await self.producer.start()
        self.logger.info(f'Subscribed to {self.config.get("KAFKA_TOPIC")} topic')

    async def send_to_dlq(self, msg, error_info):
        try:
            dlq_message = {
                'original_message': msg.value.decode('utf-8') if msg.value else None,
                'error_info': error_info,
                'topic': msg.topic,
                'partition': msg.partition,
                'offset': msg.offset,
                'timestamp': datetime.fromtimestamp(msg.timestamp / 1000).isoformat(),
                'headers': [(k, v.decode('utf-8') if v else None) for k, v in msg.headers] if msg.headers else None
            }
            
            dlq_message_json = json.dumps(dlq_message).encode('utf-8')
            
            await self.producer.send_and_wait(
                self.config.get('KAFKA_DLQ_TOPIC'),
                dlq_message_json,
                key=msg.key
            )
            self.logger.info(f"Message sent to DLQ: {msg.key}, Error: {error_info}")
            self.metrics.record_dlq_message()
        except Exception as e:
            self.logger.error(f"Failed to send message to DLQ: {e}")

    async def process_message_batch(self, messages):
        loop = asyncio.get_event_loop()
        tasks = []
        for msg in messages:
            task = asyncio.create_task(self.event_processor.process_message(msg, loop))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        for msg, (success, error_info) in zip(messages, results):
            if not success:
                await self.send_to_dlq(msg, error_info)
        
        return sum(1 for success, _ in results if success)

    async def consume_messages(self):
        self.running = True
        self.start_time = time.time()

        try:
            while self.running:
                try:
                    self.logger.debug("Attempting to fetch messages...")
                    messages = await self.consumer.getmany(timeout_ms=1000, max_records=self.batch_size)
                    self.logger.debug(f"Fetched {sum(len(batch) for batch in messages.values())} messages")
                    
                    if not messages:
                        self.empty_polls += 1
                        self.logger.info(f"No messages received. Empty poll count: {self.empty_polls}")
                        if self.empty_polls >= self.max_empty_polls:
                            self.logger.info(f"No messages received after {self.max_empty_polls} consecutive polls. Stopping.")
                            break
                        continue

                    self.empty_polls = 0  # Reset empty poll count
                    start_time = time.time()
                    processed_count = 0

                    for _, batch in messages.items():
                        processed_count += await self.process_message_batch(batch)

                    processing_time = time.time() - start_time
                    self.messages_processed += processed_count
                    self.metrics.record_metrics(processed_count, processing_time)
                    await self.consumer.commit()

                except ConsumerStoppedError:
                    self.logger.error("Kafka consumer has been stopped. Exiting consume loop.")
                    break
                except Exception as e:
                    self.logger.error(f"Unexpected error during message consumption: {e}")
                    break

        finally:
            await self.cleanup()

    async def cleanup(self):
        self.logger.info("Cleaning up resources...")
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        self.print_final_stats()

    def stop(self):
        self.running = False

    def print_final_stats(self):
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        self.logger.info(f"Total messages processed: {self.messages_processed}")
        self.logger.info(f"Total elapsed time: {elapsed_time:.2f} seconds")
        if self.messages_processed > 0:
            avg_time_per_message = elapsed_time / self.messages_processed
            self.logger.info(f"Average time per message: {avg_time_per_message:.4f} seconds")

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler('kafka_consumer.log', maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

async def main():
    logger = setup_logger()
    config = ConfigLoader(logger)
    metrics = Metrics(config, logger)

    mongodb_helper = MongoDBHelper(config={'MONGO_URI': config.get('MONGO_URI')}, logger=logger)
    event_services = EventServices(db_helper=mongodb_helper, logger=logger)
    event_processor = EventProcessor(event_services, logger)

    consumer = KafkaTradeConsumer(config, event_processor, metrics, logger)
    
    try:
        await consumer.setup_consumer()
    except Exception as e:
        logger.error(f"Failed to set up consumer: {e}")
        return

    # Set up signal handling
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Received termination signal. Stopping consumer...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda _signum, _frame: signal_handler())

    try:
        # Create tasks for consumer and stop event
        consumer_task = asyncio.create_task(consumer.consume_messages())
        stop_task = asyncio.create_task(stop_event.wait())

        # Wait for either the consumer to finish or the stop event to be set
        done, pending = await asyncio.wait(
            [consumer_task, stop_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        if consumer_task in done:
            logger.info("Consumer has finished processing all messages.")
        else:
            logger.info("Stopping consumer due to received signal.")
            consumer.stop()
            await consumer_task

        # Cancel any pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
    finally:
        await consumer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())