"""
Kafka Trade Consumer with Batch Processing

This module implements a Kafka consumer that processes trade events in batches,
using asynchronous programming and batch inserts for improved performance.

Updated: [Current Date]
Changes:
- Added type hints for improved code clarity and static type checking
- Implemented batch processing using asyncio.gather for concurrent message processing
- Integrated with EventServicesBatch for efficient batch inserts of events and outcomes
- Improved error handling and logging
- Optimized buffer flushing process
- Fixed import for List type
- Resolved indentation issues
- Added explicit buffer flushing after processing each batch
- Improved date handling in transform_message method
- Enhanced Prometheus metric recording
- Added detailed logging in process_message_batch method
- Updated to handle new flush_buffer return values
"""

import os
import uuid
import json
import logging
import signal
from datetime import datetime, timezone
from configparser import ConfigParser
from typing import Dict, Any, List
import fastjsonschema
import time
import asyncio
import aiohttp
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import ConsumerStoppedError
from prometheus_client import Counter, Histogram, CollectorRegistry, push_to_gateway
from helpers.mongodb_helper_batch import MongoDBHelperBatch
from services.event_services_batch import EventServicesBatch
from logging.handlers import RotatingFileHandler
import concurrent.futures
from pyinstrument import Profiler

# Prometheus metrics setup
REGISTRY = CollectorRegistry()
MESSAGE_COUNTER = Counter('kafka_messages_processed', 'Number of Kafka messages processed', registry=REGISTRY)
MESSAGE_LATENCY = Histogram('kafka_message_latency_seconds', 'Message processing latency in seconds', registry=REGISTRY)
DLQ_COUNTER = Counter('dlq_messages', 'Number of messages sent to dead-letter queue', registry=REGISTRY)

class ConfigLoader:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, str]:
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

    def get(self, key: str) -> str:
        return self.config.get(key, '')

class Metrics:
    def __init__(self, config: ConfigLoader, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.prometheus_available = False

    async def check_prometheus_connection(self) -> None:
        pushgateway_url = f"http://{self.config.get('PROMETHEUS_PUSHGATEWAY')}"
        max_retries = 3
        retry_delay = 2  # seconds

        async with aiohttp.ClientSession() as session:
            for attempt in range(max_retries):
                try:
                    async with session.get(pushgateway_url, timeout=5) as response:
                        if response.status == 200:
                            self.prometheus_available = True
                            self.logger.info("Successfully connected to Prometheus Pushgateway")
                            return
                except aiohttp.ClientError:
                    self.logger.warning(f"Failed to connect to Prometheus Pushgateway (attempt {attempt + 1}/{max_retries})")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)

        self.logger.warning("Unable to connect to Prometheus Pushgateway. Continuing without Prometheus metrics.")

    def record_metrics(self, num_messages: int, processing_time: float) -> None:
        if self.prometheus_available:
            MESSAGE_COUNTER.inc(num_messages)
            MESSAGE_LATENCY.observe(processing_time)
            try:
                push_to_gateway(self.config.get('PROMETHEUS_PUSHGATEWAY'), job='kafka_consumer', registry=REGISTRY)
            except Exception as e:
                self.logger.error(f"Failed to push metrics to Prometheus: {e}")

    def record_dlq_message(self) -> None:
        if self.prometheus_available:
            DLQ_COUNTER.inc()
            try:
                push_to_gateway(self.config.get('PROMETHEUS_PUSHGATEWAY'), job='kafka_consumer', registry=REGISTRY)
            except Exception as e:
                self.logger.error(f"Failed to push DLQ metric to Prometheus: {e}")

class EventProcessor:
    def __init__(self, event_services: EventServicesBatch, logger: logging.Logger):
        self.event_services = event_services
        self.logger = logger
        self.validate = self._create_validator()

    def _create_validator(self):
        schema = {
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
        return fastjsonschema.compile(schema)

    async def validate_message(self, message: Dict[str, Any]) -> bool:
        try:
            await asyncio.to_thread(self.validate, message)
            return True
        except fastjsonschema.JsonSchemaException:
            return False

    def transform_message(self, trade_event: Dict[str, Any]) -> Dict[str, Any]:
        trade_id = trade_event.get('trade_id', 'unknown')
        event_name = f"{trade_event.get('process_id', 'unknown')}"
        
        # event_name = f"{trade_event.get('process_id', 'unknown')}-{trade_id}"
        
        # Parse the timestamp and ensure it's in UTC
        event_time = datetime.fromisoformat(trade_event.get('timestamp')).replace(tzinfo=timezone.utc)
        
        return {
            'eventName': event_name,
            'tradeId': trade_id,
            'eventStatus': trade_event.get('status', 'unknown'),
            'businessDate': event_time.strftime('%Y-%m-%d'),
            'eventTime': event_time.isoformat(),
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

    async def process_message(self, msg: Any) -> tuple[bool, str]:
        try:
            trade_event = json.loads(msg.value.decode('utf-8'))
            if not await self.validate_message(trade_event):
                error_info = "Invalid message format"
                self.logger.warning(f"{error_info}: {trade_event}")
                return False, error_info

            transformed_event = self.transform_message(trade_event)
            result = self.event_services.insert_event(transformed_event)
            if result['success']:
                self.logger.debug(f"Processed and buffered event: {transformed_event}")
                return True, ""
            else:
                error_info = f"Failed to insert event: {result.get('error', 'Unknown error')}"
                self.logger.error(error_info)
                return False, error_info
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
        self.consumer: AIOKafkaConsumer = None
        self.producer: AIOKafkaProducer = None
        self.running = False
        self.start_time = None
        self.messages_processed = 0
        self.batch_size = 100
        self.empty_polls = 0
        self.max_empty_polls = 5

    async def setup_consumer(self) -> None:
        self.consumer = AIOKafkaConsumer(
            self.config.get('KAFKA_TOPIC'),
            bootstrap_servers=self.config.get('KAFKA_BOOTSTRAP_SERVERS'),
            group_id=f"{self.config.get('KAFKA_GROUP_ID')}-{uuid.uuid4()}",
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            max_poll_interval_ms=300000,  # 5 minutes
            max_poll_records=self.batch_size
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.config.get('KAFKA_BOOTSTRAP_SERVERS')
        )
        await self.consumer.start()
        await self.producer.start()
        self.logger.info(f'Subscribed to {self.config.get("KAFKA_TOPIC")} topic')

    async def send_to_dlq(self, msg: Any, error_info: str) -> None:
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

    async def process_message_batch(self, messages: List[Any]) -> int:
        self.logger.info(f"Processing batch of {len(messages)} messages")
        tasks = [self.event_processor.process_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_count = 0
        error_count = 0
        for msg, result in zip(messages, results):
            if isinstance(result, Exception):
                self.logger.error(f"Error processing message: {result}")
                await self.send_to_dlq(msg, str(result))
                error_count += 1
            else:
                success, error_info = result
                if success:
                    processed_count += 1
                else:
                    await self.send_to_dlq(msg, error_info)
                    error_count += 1
        
        self.logger.info(f"Processed {processed_count} messages successfully, {error_count} errors")
        
        # Explicitly flush the buffer after processing each batch
        self.logger.info("Flushing event buffer")
        flush_result = self.event_processor.event_services.flush_buffer()
        if not flush_result['success']:
            error_message = flush_result.get('error', 'Unknown error')
            self.logger.error(f"Error flushing event buffer: {error_message}")
            
            if 'Event insert' in error_message:
                self.logger.error(f"Event insertion error: {error_message}")
            if 'Outcome insert' in error_message:
                self.logger.error(f"Outcome insertion error: {error_message}")
            
            processed_count = 0
        else:
            self.logger.info(f"Successfully flushed buffer after processing {processed_count} messages")
            events_inserted = flush_result.get('events_inserted', 0)
            outcomes_inserted = flush_result.get('outcomes_inserted', 0)
            self.logger.info(f"Inserted {events_inserted} events and {outcomes_inserted} outcomes")
            
            if events_inserted != processed_count:
                self.logger.warning(f"Mismatch between processed messages ({processed_count}) and inserted events ({events_inserted})")
            
            if outcomes_inserted != processed_count:
                self.logger.warning(f"Mismatch between processed messages ({processed_count}) and inserted outcomes ({outcomes_inserted})")
        
        return processed_count

    async def consume_messages(self) -> None:
        self.running = True
        self.start_time = time.time()

        try:
            while self.running:
                try:
                    self.logger.debug("Attempting to fetch messages...")
                    start_fetch_time = time.time()
                    messages = await self.consumer.getmany(timeout_ms=1000, max_records=self.batch_size)
                    fetch_time = time.time() - start_fetch_time
                    total_messages = sum(len(batch) for batch in messages.values())
                    self.logger.debug(f"Fetched {total_messages} messages in {fetch_time:.2f} seconds")
                    
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
                    self.logger.info(f"Processed {processed_count} messages in {processing_time:.2f} seconds")
                    
                    commit_start_time = time.time()
                    await self.consumer.commit()
                    commit_time = time.time() - commit_start_time
                    self.logger.debug(f"Commit completed in {commit_time:.2f} seconds")

                except ConsumerStoppedError:
                    self.logger.error("Kafka consumer has been stopped. Exiting consume loop.")
                    break
                except Exception as e:
                    self.logger.error(f"Unexpected error during message consumption: {e}")
                    break

        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        self.logger.info("Cleaning up resources...")
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        
        # Ensure any remaining events in the buffer are flushed
        final_flush_result = self.event_processor.event_services.flush_buffer()
        if not final_flush_result['success']:
            self.logger.error(f"Error in final buffer flush: {final_flush_result.get('error', 'Unknown error')}")
        else:
            self.logger.info("Final buffer flush completed successfully")
        
        self.print_final_stats()

    def stop(self) -> None:
        self.running = False

    def print_final_stats(self) -> None:
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        self.logger.info(f"Total messages processed: {self.messages_processed}")
        self.logger.info(f"Total elapsed time: {elapsed_time:.2f} seconds")
        if self.messages_processed > 0:
            avg_time_per_message = elapsed_time / self.messages_processed
            self.logger.info(f"Average time per message: {avg_time_per_message:.4f} seconds")

def setup_logger() -> logging.Logger:
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

async def main() -> None:
    logger = setup_logger()
    config = ConfigLoader(logger)
    metrics = Metrics(config, logger)
    
    await metrics.check_prometheus_connection()

    mongodb_helper = MongoDBHelperBatch(config={'MONGO_URI': config.get('MONGO_URI')}, logger=logger)
    event_services = EventServicesBatch(db_helper=mongodb_helper, logger=logger)
    event_processor = EventProcessor(event_services, logger)

    consumer = KafkaTradeConsumer(config, event_processor, metrics, logger)
    
    try:
        await consumer.setup_consumer()
    except Exception as e:
        logger.error(f"Failed to set up consumer: {e}")
        return

    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Received termination signal. Stopping consumer...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda _signum, _frame: signal_handler())

    try:
        consumer_task = asyncio.create_task(consumer.consume_messages())
        stop_task = asyncio.create_task(stop_event.wait())

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

        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
    finally:
        event_services.flush_buffer()
        await consumer.cleanup()

if __name__ == "__main__":
    profiler = Profiler()
    profiler.start()
    asyncio.run(main())
    profiler.stop()
    
    print("\nProfiling Results:")
    print(profiler.output_text(color=True))