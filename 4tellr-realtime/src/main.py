import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import signal
import logging
from logging.handlers import RotatingFileHandler
from pyinstrument import Profiler
from src.metrics.metrics_handler import Metrics
from src.config.config_loader import ConfigLoader
from src.processing.event_processor import EventProcessor
from src.consumer.kafka_consumer import KafkaTradeConsumer
from src.helpers.mongodb_helper_batch import MongoDBHelperBatch
from src.services.event_services_batch import EventServicesBatch




def setup_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler('kafka_consumer.log', maxBytes=10000000, backupCount=5)
    console_handler = logging.StreamHandler()
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
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
