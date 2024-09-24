"""
Drop Kafka Topic Script

This script is designed to delete a specified Kafka topic. It reads the Kafka configuration from
a JSON file and uses the Confluent Kafka Admin Client to delete the topic.

Usage:
    python drop_kafka_topic.py [topic_name]

Arguments:
    topic_name (optional): The name of the topic to be deleted. If not provided, the script will
                           display a message and exit.

Configuration:
    Requires a 'config.json' file in the same directory with the following key:
    - 'kafka_bootstrap_servers': Kafka bootstrap servers

Example:
    python drop_kafka_topic.py my_topic_name

Requirements:
    - Python 3.6+
    - confluent-kafka library
    - Kafka cluster accessible with admin permissions

Note: Ensure you have the necessary permissions to delete topics on your Kafka cluster.
      Use this script with caution as it permanently deletes the specified topic.
"""

from confluent_kafka.admin import AdminClient
from confluent_kafka.error import KafkaError
import json
import logging
import os
import time
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(file_path):
    """
    Load configuration from a JSON file.

    Args:
    file_path (str): Path to the JSON configuration file

    Returns:
    dict: Loaded configuration

    Raises:
    FileNotFoundError: If the config file is not found
    """
    logging.info(f"Loading configuration from {file_path}")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, file_path)
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def delete_topic(admin_client, topic_name):
    """
    Delete a Kafka topic.

    Args:
    admin_client (AdminClient): Kafka Admin Client instance
    topic_name (str): Name of the topic to be deleted

    Returns:
    None
    """
    futures = admin_client.delete_topics([topic_name])
    for topic, future in futures.items():
        try:
            future.result()
            logging.info(f"Topic {topic} deleted successfully.")
        except KafkaError as e:
            if e.args[0].code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                logging.info(f"Topic {topic} does not exist. Skipping deletion.")
            else:
                logging.error(f"Failed to delete topic {topic}: {e}")

def drop_kafka_topic(config, topic_name):
    """
    Drop the specified Kafka topic using the provided configuration.

    Args:
    config (dict): Kafka configuration containing bootstrap servers
    topic_name (str): Name of the topic to be deleted

    Returns:
    None
    """
    admin_client = AdminClient({"bootstrap.servers": config['kafka_bootstrap_servers']})

    logging.info(f"Attempting to drop topic: {topic_name}")
    delete_topic(admin_client, topic_name)

    # Wait for a short period to ensure the deletion is processed
    time.sleep(5)
    logging.info(f"Topic {topic_name} has been dropped.")

def main():
    """
    Main function to load config, get topic name from command line, and initiate the topic deletion process.
    """
    try:
        if len(sys.argv) < 2:
            print("Usage: python drop_kafka_topic.py <topic_name>")
            print("Please provide a topic name as an argument.")
            return

        topic_name = sys.argv[1]
        config = load_config("config.json")
        drop_kafka_topic(config, topic_name)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()