import asyncio
import time
import uuid
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import ConsumerStoppedError
import logging
from typing import List, Any
import json
from datetime import datetime

class KafkaTradeConsumer:
    def __init__(self, config, event_processor, metrics, logger: logging.Logger):
        self.config = config
        self.event_processor = event_processor
        self.metrics = metrics
        self.logger = logger
        self.consumer = None
        self.producer = None
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
            max_poll_interval_ms=300000,
            max_poll_records=self.batch_size
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.config.get('KAFKA_BOOTSTRAP_SERVERS')
        )
        await self.consumer.start()
        await self.producer.start()
        self.logger.info(f"Subscribed to {self.config.get('KAFKA_TOPIC')} topic")

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
        for msg, result in zip(messages, results):
            if isinstance(result, Exception):
                self.logger.error(f"Error processing message: {result}")
                await self.send_to_dlq(msg, str(result))
            else:
                success, error_info = result
                if success:
                    processed_count += 1
                else:
                    await self.send_to_dlq(msg, error_info)
        
        return processed_count

    async def consume_messages(self) -> None:
        self.running = True
        self.start_time = time.time()

        try:
            while self.running:
                try:
                    messages = await self.consumer.getmany(timeout_ms=1000, max_records=self.batch_size)
                    
                    if not messages:
                        self.empty_polls += 1
                        if self.empty_polls >= self.max_empty_polls:
                            self.logger.info(f"No messages after {self.max_empty_polls} polls. Stopping.")
                            break
                        continue

                    self.empty_polls = 0
                    start_time = time.time()
                    processed_count = 0

                    for _, batch in messages.items():
                        processed_count += await self.process_message_batch(batch)

                    processing_time = time.time() - start_time
                    self.messages_processed += processed_count
                    self.metrics.record_metrics(processed_count, processing_time)
                    
                    await self.consumer.commit()

                except ConsumerStoppedError:
                    self.logger.error("Consumer stopped. Exiting consume loop.")
                    break
                except Exception as e:
                    self.logger.error(f"Unexpected error during consumption: {e}")
                    break

        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        self.logger.info("Cleaning up resources...")
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        self.print_final_stats()

    def stop(self) -> None:
        self.running = False

    def print_final_stats(self) -> None:
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        self.logger.info(f"Total messages processed: {self.messages_processed}")
        self.logger.info(f"Total elapsed time: {elapsed_time:.2f} seconds")
        if self.messages_processed > 0:
            avg_time = elapsed_time / self.messages_processed
            self.logger.info(f"Average time per message: {avg_time:.4f} seconds")