"""
Create Kafka Topic

This script creates a new Kafka topic with the specified name. It allows you to set
the number of partitions and replication factor for the topic.

Usage:
    python create_kafka_topic.py <topic_name> [num_partitions] [replication_factor] [bootstrap_servers]

Arguments:
    topic_name: Name of the Kafka topic to create
    num_partitions: Number of partitions for the topic (optional, default: 1)
    replication_factor: Replication factor for the topic (optional, default: 1)
    bootstrap_servers: Kafka bootstrap servers (optional, default: localhost:9092)

Example:
    python create_kafka_topic.py my_new_topic
    python create_kafka_topic.py my_new_topic 3 2 kafka1:9092,kafka2:9092

Requirements:
    - Python 3.6+
    - confluent-kafka library

Note: Ensure you have the necessary permissions to create topics on the Kafka cluster.
"""

import sys
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaError

def create_topic(topic_name, num_partitions, replication_factor, bootstrap_servers):
    """
    Create a new Kafka topic with the specified parameters.

    Args:
    topic_name (str): Name of the topic to create
    num_partitions (int): Number of partitions for the topic
    replication_factor (int): Replication factor for the topic
    bootstrap_servers (str): Kafka bootstrap servers

    Returns:
    None
    """
    # Create AdminClient
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})

    # Create NewTopic object
    new_topic = NewTopic(
        topic_name,
        num_partitions=num_partitions,
        replication_factor=replication_factor
    )

    # Create the topic
    fs = admin_client.create_topics([new_topic])

    # Wait for topic creation to complete and handle any errors
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print(f"Topic '{topic}' created successfully.")
        except KafkaError as e:
            if e.args[0].code() == KafkaError.TOPIC_ALREADY_EXISTS:
                print(f"Topic '{topic}' already exists.")
            else:
                print(f"Failed to create topic '{topic}': {e}")

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 5:
        print("Usage: python create_kafka_topic.py <topic_name> [num_partitions] [replication_factor] [bootstrap_servers]")
        sys.exit(1)

    topic_name = sys.argv[1]
    num_partitions = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    replication_factor = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    bootstrap_servers = sys.argv[4] if len(sys.argv) > 4 else "localhost:9092"

    print(f"Creating Kafka topic '{topic_name}'")
    print(f"Number of partitions: {num_partitions}")
    print(f"Replication factor: {replication_factor}")
    print(f"Using bootstrap servers: {bootstrap_servers}")

    create_topic(topic_name, num_partitions, replication_factor, bootstrap_servers)

if __name__ == "__main__":
    main()