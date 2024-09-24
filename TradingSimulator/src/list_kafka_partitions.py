"""
Kafka Topic Partition Lister

This script connects to a Kafka cluster and retrieves partition information for a specified topic.
It displays the total number of partitions and detailed information about each partition,
including the leader, replicas, and in-sync replicas (ISRs).

Usage:
    python list_kafka_partitions.py <topic_name> [bootstrap_servers]

Arguments:
    topic_name: Name of the Kafka topic to inspect
    bootstrap_servers: Kafka bootstrap servers (optional, defaults to localhost:9092)

Example:
    python list_kafka_partitions.py my_topic
    python list_kafka_partitions.py my_topic kafka1:9092,kafka2:9092

Requirements:
    - Python 3.6+
    - confluent-kafka library

Note: Ensure you have the necessary permissions to access the Kafka cluster and topic metadata.
"""

import sys
from confluent_kafka.admin import AdminClient
from confluent_kafka import KafkaException

def list_topic_partitions(bootstrap_servers, topic_name):
    """
    Retrieve and display partition information for a specified Kafka topic.

    Args:
    bootstrap_servers (str): Kafka bootstrap servers
    topic_name (str): Name of the Kafka topic to inspect

    Returns:
    None
    """
    # Create AdminClient
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})

    try:
        # Get topic metadata
        metadata = admin_client.list_topics(topic=topic_name, timeout=10)

        # Check if the topic exists
        if topic_name not in metadata.topics:
            print(f"Topic '{topic_name}' does not exist.")
            return

        # Get partition information
        topic_info = metadata.topics[topic_name]
        partitions = topic_info.partitions

        # Print results
        print(f"Topic: {topic_name}")
        print(f"Number of partitions: {len(partitions)}")
        print("\nPartition details:")
        for partition_id, partition_info in partitions.items():
            print(f"  Partition {partition_id}:")
            print(f"    Leader: {partition_info.leader}")
            print(f"    Replicas: {partition_info.replicas}")
            print(f"    ISRs: {partition_info.isrs}")

    except KafkaException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python list_kafka_partitions.py <topic_name> [bootstrap_servers]")
        print("If bootstrap_servers is not provided, it defaults to localhost:9092")
        sys.exit(1)

    topic_name = sys.argv[1]
    bootstrap_servers = sys.argv[2] if len(sys.argv) == 3 else "localhost:9092"

    print(f"Using bootstrap servers: {bootstrap_servers}")
    list_topic_partitions(bootstrap_servers, topic_name)