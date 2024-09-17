import sys
from os.path import dirname, abspath
from datetime import datetime
import uuid
from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import logging
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
from typing import Dict, Any
import signal
import os
from jsonschema import validate
import time

# Ensure the project directory is in the Python path
project_dir = dirname(dirname(abspath(__file__)))
sys.path.append(project_dir)

from helpers.mongodb_helper import MongoDBHelper
from services.event_services import EventServices

# Configure logging
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler('kafka_consumer.log', maxBytes=10000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logger()

# Load configuration
def load_config():
    config = ConfigParser()
    config.read('config.txt')
    return {
        'MONGO_URI': os.environ.get('MONGO_URI', config.get('DEFAULT', 'MONGO_URI')),
        'KAFKA_BOOTSTRAP_SERVERS': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', config.get('KAFKA', 'BOOTSTRAP_SERVERS')),
        'KAFKA_TOPIC': os.environ.get('KAFKA_TOPIC', config.get('KAFKA', 'TOPIC')),
        'KAFKA_GROUP_ID': os.environ.get('KAFKA_GROUP_ID', config.get('KAFKA', 'GROUP_ID')),
    }

config = load_config()

# Kafka consumer configuration
kafka_conf = {
    'bootstrap.servers': config['KAFKA_BOOTSTRAP_SERVERS'],
    'group.id': f"{config['KAFKA_GROUP_ID']}-{uuid.uuid4()}",
    'auto.offset.reset': 'earliest',
    'max.poll.interval.ms': 600000
}

# Initialize services
mongodb_helper = MongoDBHelper(config={'MONGO_URI': config['MONGO_URI']}, logger=logger)
event_services = EventServices(db_helper=mongodb_helper, logger=logger)

# Metrics
messages_processed = 0
total_processing_time = 0

# Message schema
MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "process_id": {"type": "string"},
        "trade_id": {"type": "integer"},
        "status": {"type": "string"},
        "timestamp": {"type": "string"},
        "application": {"type": "string"}
    },
    "required": [ "trade_id", "status", "timestamp"]
}

def validate_message(message: Dict[str, Any]) -> bool:
    try:
        validate(instance=message, schema=MESSAGE_SCHEMA)
        return True
    except Exception as e:
        logger.error(f"Message validation failed: {e}")
        return False

def transform_message(trade_event: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'eventName': trade_event.get('process_id', 'unknown'),
        'tradeId': trade_event.get('trade_id', 'unknown'),
        'eventStatus': trade_event.get('status', 'unknown'),
        'businessDate': datetime.now().strftime('%Y-%m-%d'),
        'eventTime': trade_event.get('timestamp', 'unknown'),
        'eventType': 'MESSAGE',
        'batchOrRealtime': 'Realtime',
        'resource': 'trading app',
        'message': '',
        'details': {
            'messageId': trade_event.get('trade_id', 'unknown'),
            'messageQueue': 'trade_events',
            'application': trade_event.get('application', 'unknown')
        }
    }

def process_message(msg: Any) -> None:
    global messages_processed, total_processing_time
    start_time = time.time()
    
    trade_event = json.loads(msg.value().decode('utf-8'))
    logger.info(f'Received trade event: {trade_event}')

    if not validate_message(trade_event):
        logger.error(f"Invalid message received: {trade_event}")
        return

    transformed_event = transform_message(trade_event)
    event_services.insert_event(transformed_event)
    logger.info(f'Processed and inserted event: {transformed_event}')
    
    messages_processed += 1
    processing_time = time.time() - start_time
    total_processing_time += processing_time
    
    # Log metrics every 100 messages
    if messages_processed % 100 == 0:
        avg_processing_time = total_processing_time / messages_processed
        logger.info(f"Metrics - Messages Processed: {messages_processed}, Avg Processing Time: {avg_processing_time:.4f} seconds")

def consume_messages(consumer: Consumer, running: bool) -> None:
    try:
        while running():
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info('End of partition reached {0}/{1}'.format(msg.topic(), msg.partition()))
                else:
                    raise KafkaException(msg.error())
            else:
                process_message(msg)
    except KafkaException as e:
        logger.error(f'Kafka exception: {e}')
    except Exception as e:
        logger.error(f'Unexpected exception: {e}')
    finally:
        consumer.close()
        logger.info('Kafka consumer closed')

def main():
    running = True
    def signal_handler(signum, frame):
        nonlocal running
        logger.info('Interrupt received, stopping consumer...')
        running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    consumer = Consumer(kafka_conf)
    consumer.subscribe([config['KAFKA_TOPIC']])
    logger.info(f'Subscribed to {config["KAFKA_TOPIC"]} topic')

    consume_messages(consumer, lambda: running)

if __name__ == "__main__":
    main()