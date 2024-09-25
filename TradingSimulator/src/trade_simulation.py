"""
Trade Simulation Script

This script simulates continuous trade processing and publishes trade events to a Kafka topic.
It generates a specified number of trades per second, processes them through defined steps,
and sends messages to Kafka for each trade and step event.

Usage:
    python trade_simulation.py

Configuration:
    - Requires a 'config.json' file in the same directory with Kafka configuration
      and trades_per_second setting
    - Requires a 'trading.json' file in the 'configs' subdirectory with trade processing steps

Example:
    python trade_simulation.py

Requirements:
    - Python 3.6+
    - confluent-kafka library
    - Kafka cluster accessible with write permissions to the specified topic

Note: Ensure your Kafka cluster is running and accessible before starting the simulation.
      This script runs indefinitely until interrupted (Ctrl+C).
"""

import json
import time
import threading
import logging
import os
from datetime import datetime, timedelta
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_process_steps(file_path):
    """
    Load trade processing steps from a JSON file.

    Args:
    file_path (str): Path to the JSON file containing process steps

    Returns:
    dict: Loaded process steps
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(root_dir, 'src', 'configs', file_path)
    logging.info(f"Loading process steps from {full_path}")
    with open(full_path, 'r') as f:
        return json.load(f)

def load_config(file_path):
    """
    Load configuration from a JSON file.

    Args:
    file_path (str): Path to the JSON configuration file

    Returns:
    dict: Loaded configuration

    Raises:
    KeyError: If required configuration keys are missing
    """
    logging.info(f"Loading configuration from {file_path}")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(root_dir, file_path)
    with open(config_path, 'r') as f:
        config = json.load(f)
    required_keys = ['kafka_bootstrap_servers', 'kafka_topic']
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing required configuration key: {key}")
    return config

def create_kafka_producer(bootstrap_servers):
    """
    Create a Confluent Kafka producer.

    Args:
    bootstrap_servers (str): Kafka bootstrap servers

    Returns:
    Producer: Confluent Kafka producer instance
    """
    logging.info(f"Creating Kafka producer with bootstrap servers: {bootstrap_servers}")
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'client.id': 'trade_simulator'
    }
    return Producer(conf)

def delivery_report(err, msg):
    """
    Callback function for Kafka producer to report on message delivery.

    Args:
    err: Error (if any) during message delivery
    msg: Successfully delivered message
    """
    if err is not None:
        logging.error(f'Message delivery failed: {err}')
    else:
        logging.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def publish_message(producer, topic, message, max_retries=3, retry_delay=1):
    """
    Publish a message to Kafka with retry mechanism.

    Args:
    producer (Producer): Kafka producer instance
    topic (str): Kafka topic to publish to
    message (dict): Message to be published
    max_retries (int): Maximum number of retry attempts
    retry_delay (int): Delay between retry attempts in seconds

    Returns:
    bool: True if message was published successfully, False otherwise
    """
    serializer = StringSerializer('utf_8')
    for attempt in range(max_retries):
        try:
            producer.produce(
                topic,
                key=str(message.get('trade_id', '')),
                value=serializer(json.dumps(message)),
                on_delivery=delivery_report
            )
            producer.poll(0)  # Trigger any available delivery report callbacks
            return True
        except Exception as e:
            logging.error(f"Error publishing message (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logging.error("Max retries reached. Message not published.")
                return False

def process_trade(trade_id, steps, producer, topic):
    """
    Simulate the processing of a single trade.

    Args:
    trade_id (int): Unique identifier for the trade
    steps (list): List of processing steps for the trade
    producer (Producer): Kafka producer instance
    topic (str): Kafka topic to publish trade events
    """
    start_time = datetime.now()
    logging.info(f"Starting trade {trade_id} at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Send trade start message
    start_message = {
        "trade_id": trade_id,
        "status": "STARTED",
        "timestamp": start_time.isoformat(),
        "process_id": f"TRADE_START--{trade_id}"
    }
    publish_message(producer, topic, start_message)

    for step in steps:
        # Send step start message
        step_start_message = {
            "trade_id": trade_id,
            "process_id": step['process_id'],
            "application": step['application'],
            "status": "STARTED",
            "timestamp": datetime.now().isoformat()
        }
        publish_message(producer, topic, step_start_message)
        logging.info(f"Trade {trade_id} - {step['process_id']} started by {step['application']}")

        # Simulate the processing time
        process_time = int(step["processing_time"].split()[0]) / 1000 if "ms" in step["processing_time"] else 0
        if process_time > 0:
            time.sleep(process_time)

        # Simulate scheduled time processing
        scheduled_time = step.get("scheduled_time")
        if scheduled_time:
            # Calculate the actual scheduled datetime
            current_time = datetime.now()
            delta = timedelta(days=int(scheduled_time.split()[0].replace("T+", "")))
            scheduled_datetime = start_time + delta + timedelta(hours=int(scheduled_time.split()[1].split(':')[0]),
                                                                minutes=int(scheduled_time.split()[1].split(':')[1]),
                                                                seconds=int(scheduled_time.split()[1].split(':')[2]))
            if scheduled_datetime > current_time:
                time_to_wait = (scheduled_datetime - current_time).total_seconds()
                logging.info(f"Waiting for scheduled time: {scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(time_to_wait)

        # Send step completion message
        step_complete_message = {
            "trade_id": trade_id,
            "process_id": step['process_id'],
            "application": step['application'],
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat()
        }
        publish_message(producer, topic, step_complete_message)
        logging.info(f"Trade {trade_id} - {step['process_id']} completed by {step['application']}")

    # Send trade completion message
    completion_message = {
        "trade_id": trade_id,
        "status": "SUCCESS",
        "timestamp": datetime.now().isoformat()
    }
    logging.info(f"Trade {trade_id} completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    publish_message(producer, topic, completion_message)

def generate_trades(steps, trades_per_second, config):
    """
    Generate and process trades continuously based on the specified configuration.

    Args:
    steps (list): List of processing steps for each trade
    trades_per_second (int): Number of trades to generate per second
    config (dict): Kafka configuration
    """
    trade_id = 1
    producer = None

    while True:
        try:
            if producer is None:
                producer = create_kafka_producer(config['kafka_bootstrap_servers'])
                logging.info(f"Connected to Kafka at {config['kafka_bootstrap_servers']}")

            threads = []
            for _ in range(trades_per_second):
                thread = threading.Thread(target=process_trade, args=(trade_id, steps, producer, config['kafka_topic']))
                threads.append(thread)
                thread.start()
                trade_id += 1

            for thread in threads:
                thread.join()

            time.sleep(1)

        except Exception as e:
            logging.error(f"Kafka error: {e}")
            logging.info("Attempting to reconnect...")
            if producer:
                producer.flush()
            producer = None
            time.sleep(5)  # Wait before attempting to reconnect

def main():
    """
    Main function to load config, steps, and start continuous trade processing.
    """
    logging.info("Starting trade simulation script")
    try:
        steps = load_process_steps("trading.json")
        config = load_config("config.json")

        trades_per_second = config.get("trades_per_second", 1)
        logging.info(f"Simulating {trades_per_second} trades per second.")
        logging.info(f"Kafka Configuration:")
        logging.info(f"  Bootstrap Servers: {config['kafka_bootstrap_servers']}")
        logging.info(f"  Topic: {config['kafka_topic']}")

        generate_trades(steps, trades_per_second, config)
    except KeyError as e:
        logging.error(f"Configuration error: {e}")
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON: {e}")
    except KeyboardInterrupt:
        logging.info("Stopping trade simulation...")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
