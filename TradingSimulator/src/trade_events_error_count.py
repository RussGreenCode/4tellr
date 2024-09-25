import json
from confluent_kafka import Consumer, KafkaError

def load_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    required_keys = ['kafka_bootstrap_servers', 'group_id']
    for key in required_keys:
        if key not in config:
            config[key] = 'localhost:9092'  # Default value
    return config

def count_trade_events(bootstrap_servers, group_id):
    consumer_config = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False  # Disable auto commit of offsets
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe(['trade_events_errors'])

    message_count = 0
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                if message_count > 0:  # Exit if no more messages and at least one message was counted
                    break
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Error while consuming message: {msg.error()}")
                    break
            message_count += 1
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

    print(f"Total trade events consumed: {message_count}")

def main():
    config = load_config("config.json")
    count_trade_events(config['kafka_bootstrap_servers'], config['group_id'])

if __name__ == "__main__":
    main()
