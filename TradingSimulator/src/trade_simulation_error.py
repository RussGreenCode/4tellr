"""
Trade Simulation Error Custom Script

This script is a modified version of trade_simulation_custom.py designed to generate
incorrect messages for testing dead letter queue processing. It intentionally
introduces errors in the messages sent to Kafka.

Usage:
    python trade_simulation_error_custom.py <number_of_trades>

Arguments:
    number_of_trades: The total number of trades to simulate

Configuration:
    - Requires a 'config.json' file in the same directory with Kafka configuration
    - Requires a 'trading.json' file in the 'configs' subdirectory with trade processing steps

Example:
    python trade_simulation_error_custom.py 100

Requirements:
    - Python 3.6+
    - confluent-kafka library
    - Kafka cluster accessible with write permissions to the specified topic

Note: Ensure your Kafka cluster is running and accessible before starting the simulation.
"""

import json
import time
import threading
import logging
import os
import sys
import random
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
        'client.id': 'trade_simulator_error'
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
    This version intentionally introduces errors in some messages.

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
    
    # Introduce random errors
    if random.random() < 0.3:  # 30% chance of error
        error_type = random.choice(['empty_trade_id', 'invalid_json', 'missing_field', 'invalid_timestamp'])
        if error_type == 'empty_trade_id':
            message['trade_id'] = ''
        elif error_type == 'invalid_json':
            message = "This is not valid JSON"
        elif error_type == 'missing_field':
            message.pop('status', None)
        elif error_type == 'invalid_timestamp':
            message['timestamp'] = 'not_a_timestamp'
        
        logging.info(f"Introducing error: {error_type}")

    for attempt in range(max_retries):
        try:
            producer.produce(
                topic,
                key=str(message.get('trade_id', '')),
                value=serializer(json.dumps(message) if isinstance(message, dict) else str(message)),
                on_delivery=delivery_report
            )
            producer.poll(0)
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
    Simulate the processing of a single trade with potential errors.

    Args:
    trade_id (int): Unique identifier for the trade
    steps (list): List of processing steps for the trade
    producer (Producer): Kafka producer instance
    topic (str): Kafka topic to publish trade events
    """
    start_time = datetime.now()
    logging.info(f"Starting trade {trade_id} at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Send trade start message (potentially with errors)
    start_message = {
        "trade_id": trade_id,
        "status": "STARTED",
        "timestamp": start_time.isoformat()
    }
    publish_message(producer, topic, start_message)

    for step in steps:
        # Send step start message (potentially with errors)
        step_start_message = {
            "trade_id": trade_id,
            "process_id": step['process_id'],
            "application": step['application'],
            "status": "STARTED",
            "timestamp": datetime.now().isoformat()
        }
        publish_message(producer, topic, step_start_message)
        logging.info(f"Trade {trade_id} - {step['process_id']} started by {step['application']}")

        # Simulate processing time
        time.sleep(random.uniform(0.1, 1.0))

        # Send step completion message (potentially with errors)
        step_complete_message = {
            "trade_id": trade_id,
            "process_id": step['process_id'],
            "application": step['application'],
            "status": "SUCCESS",
            "timestamp": datetime.now().isoformat()
        }
        publish_message(producer, topic, step_complete_message)
        logging.info(f"Trade {trade_id} - {step['process_id']} completed by {step['application']}")

    # Send trade completion message (potentially with errors)
    completion_message = {
        "trade_id": trade_id,
        "status": "SUCCESS",
        "timestamp": datetime.now().isoformat()
    }
    logging.info(f"Trade {trade_id} completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    publish_message(producer, topic, completion_message)

def generate_trades(steps, trades_per_second, config, num_trades):
    """
    Generate and process trades based on the specified configuration.

    Args:
    steps (list): List of processing steps for each trade
    trades_per_second (int): Number of trades to generate per second
    config (dict): Kafka configuration
    num_trades (int): Total number of trades to generate
    """
    trade_id = 1
    producer = None
    trades_generated = 0

    try:
        while trades_generated < num_trades:
            try:
                if producer is None:
                    producer = create_kafka_producer(config['kafka_bootstrap_servers'])
                    logging.info(f"Connected to Kafka at {config['kafka_bootstrap_servers']}")

                threads = []
                trades_to_generate = min(trades_per_second, num_trades - trades_generated)
                for _ in range(trades_to_generate):
                    thread = threading.Thread(target=process_trade, args=(trade_id, steps, producer, config['kafka_topic']))
                    threads.append(thread)
                    thread.start()
                    trade_id += 1
                    trades_generated += 1

                for thread in threads:
                    thread.join()

                if trades_generated < num_trades:
                    time.sleep(1)

            except Exception as e:
                logging.error(f"Kafka error: {e}")
                logging.info("Attempting to reconnect...")
                if producer:
                    producer.flush()
                producer = None
                time.sleep(5)  # Wait before attempting to reconnect

        logging.info(f"Generated {trades_generated} trades with potential errors. Simulation complete.")
    finally:
        if producer:
            logging.info("Flushing Kafka producer...")
            producer.flush()
            logging.info("Kafka producer flushed.")

def main():
    """
    Main function to load config, steps, and start trade processing with errors.
    """
    logging.info("Starting trade simulation error script")
    try:
        if len(sys.argv) != 2:
            print("Usage: python trade_simulation_error_custom.py <number_of_trades>")
            sys.exit(1)

        num_trades = int(sys.argv[1])
        steps = load_process_steps("trading.json")
        config = load_config("config.json")

        trades_per_second = config.get("trades_per_second", 1)
        logging.info(f"Simulating {num_trades} trades with potential errors at {trades_per_second} trades per second.")
        logging.info(f"Kafka Configuration:")
        logging.info(f"  Bootstrap Servers: {config['kafka_bootstrap_servers']}")
        logging.info(f"  Topic: {config['kafka_topic']}")

        generate_trades(steps, trades_per_second, config, num_trades)
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