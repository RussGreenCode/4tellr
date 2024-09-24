import json
from confluent_kafka.admin import AdminClient

def load_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    required_keys = ['kafka_bootstrap_servers']
    for key in required_keys:
        if key not in config:
            config[key] = 'localhost:9092'  # Default value
    return config

def list_kafka_topics(bootstrap_servers):
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    topics = admin_client.list_topics().topics
    print("Available Kafka topics:")
    for topic in topics:
        print(f"  - {topic}")

def main():
    config = load_config("config.json")
    list_kafka_topics(config['kafka_bootstrap_servers'])

if __name__ == "__main__":
    main()
