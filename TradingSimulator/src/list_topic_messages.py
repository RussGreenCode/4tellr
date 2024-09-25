"""
List Kafka Topic Messages

This script connects to a Kafka cluster and retrieves the first N messages from a specified topic,
starting from the earliest available offset. It exits after reading all available messages or
reaching the requested number of messages.

Usage:
    python list_topic_messages.py <topic_name> <number_of_messages> [bootstrap_servers]

Arguments:
    topic_name: Name of the Kafka topic to read messages from
    number_of_messages: Number of messages to retrieve and display
    bootstrap_servers: Kafka bootstrap servers (optional, defaults to localhost:9092)

Example:
    python list_topic_messages.py my_topic 10
    python list_topic_messages.py my_topic 5 kafka1:9092,kafka2:9092

Requirements:
    - Python 3.6+
    - confluent-kafka library

Note: Ensure you have the necessary permissions to access the Kafka cluster and read from the specified topic.
"""

import sys
import json
from confluent_kafka import Consumer, KafkaError, KafkaException, TopicPartition

def load_config(bootstrap_servers):
    """
    Create a configuration dictionary for the Kafka consumer.

    Args:
    bootstrap_servers (str): Kafka bootstrap servers

    Returns:
    dict: Kafka consumer configuration
    """
    return {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'message_lister_' + str(hash(bootstrap_servers)),  # Unique group ID
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,  # Disable auto commit
        'session.timeout.ms': 6000,
    }

def list_messages(topic, num_messages, bootstrap_servers):
    """
    List the first N messages from the specified Kafka topic, starting from the earliest offset.

    Args:
    topic (str): Name of the Kafka topic
    num_messages (int): Number of messages to retrieve and display
    bootstrap_servers (str): Kafka bootstrap servers

    Returns:
    None
    """
    config = load_config(bootstrap_servers)
    consumer = Consumer(config)
    
    try:
        print(f"Attempting to subscribe to topic: {topic}")
        consumer.subscribe([topic])
        print(f"Successfully subscribed to topic: {topic}")
        
        # Get metadata about the topic
        cluster_metadata = consumer.list_topics(topic=topic)
        topic_metadata = cluster_metadata.topics[topic]
        partitions = topic_metadata.partitions
        print(f"Topic {topic} has {len(partitions)} partition(s)")
        
        # Manually assign to the beginning of each partition
        for partition_id in partitions:
            tp = TopicPartition(topic, partition_id, 0)  # 0 is the earliest offset
            consumer.assign([tp])
            low, high = consumer.get_watermark_offsets(tp)
            print(f"Partition {partition_id}: Low offset = {low}, High offset = {high}")
        
    except KafkaException as e:
        print(f"Error setting up consumer: {e}")
        consumer.close()
        return

    messages_read = 0
    consecutive_empty_polls = 0
    max_empty_polls = 5  # Exit after 5 consecutive empty polls

    try:
        while messages_read < num_messages and consecutive_empty_polls < max_empty_polls:
            try:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    consecutive_empty_polls += 1
                    continue
                
                consecutive_empty_polls = 0  # Reset the counter when we receive a message
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print(f"Reached end of partition {msg.partition()} for topic {msg.topic()}")
                        continue
                    else:
                        print(f"Error: {msg.error()}")
                        break
                
                key = msg.key().decode('utf-8') if msg.key() else "None"
                try:
                    value = json.loads(msg.value().decode('utf-8'))
                    value = json.dumps(value, indent=2)
                except json.JSONDecodeError:
                    value = msg.value().decode('utf-8')

                print(f"Message {messages_read + 1}:")
                print(f"  Key: {key}")
                print(f"  Value: {value}")
                print(f"  Partition: {msg.partition()}")
                print(f"  Offset: {msg.offset()}")
                print()

                messages_read += 1

            except KafkaException as e:
                print(f"Kafka error: {e}")
                break

        if messages_read == 0:
            print(f"No messages found in topic '{topic}'.")
        elif messages_read < num_messages:
            print(f"Retrieved all available messages. Total: {messages_read} messages from topic '{topic}'.")
        else:
            print(f"Retrieved {messages_read} messages from topic '{topic}'.")

    finally:
        consumer.close()
        print("Consumer closed.")

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python list_topic_messages.py <topic_name> <number_of_messages> [bootstrap_servers]")
        print("If bootstrap_servers is not provided, it defaults to localhost:9092")
        sys.exit(1)

    topic_name = sys.argv[1]
    num_messages = int(sys.argv[2])
    bootstrap_servers = sys.argv[3] if len(sys.argv) == 4 else "localhost:9092"

    print(f"Listing up to {num_messages} messages from topic '{topic_name}'")
    print(f"Using bootstrap servers: {bootstrap_servers}")
    list_messages(topic_name, num_messages, bootstrap_servers)
    print("Script execution completed.")

if __name__ == "__main__":
    main()