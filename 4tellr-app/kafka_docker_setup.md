# Setting up Kafka using Docker

This guide will walk you through the process of setting up a Kafka instance using Docker, which is useful for development and testing purposes.

## Prerequisites

- Docker and Docker Compose installed on your system
- Basic understanding of Docker and containerization
- Familiarity with Kafka concepts

## Step 1: Create a Docker Compose File

Create a file named `docker-compose-kafka.yml` in your project directory with the following content:

```yaml
version: '3'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "22181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "29092:29092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    depends_on:
      - kafka
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
```

This Docker Compose file defines three services:
1. Zookeeper: Required for Kafka cluster management
2. Kafka: The actual Kafka broker
3. Kafka UI: A web interface for managing and monitoring Kafka

## Step 2: Start the Docker Containers

Run the following command in the directory containing your `docker-compose-kafka.yml` file:

```bash
docker-compose -f docker-compose-kafka.yml up -d
```

This command will download the necessary Docker images and start the Zookeeper, Kafka, and Kafka UI containers in detached mode.

## Step 3: Verify the Setup

1. Check if the containers are running:
   ```bash
   docker-compose -f docker-compose-kafka.yml ps
   ```
   You should see all three services (zookeeper, kafka, and kafka-ui) in the "Up" state.

2. Access Kafka UI:
   Open a web browser and navigate to `http://localhost:8080`. You should see the Kafka UI interface.

## Step 4: Create a Topic

You can create a Kafka topic using the Kafka UI or by running a command in the Kafka container:

Using Docker command:
```bash
docker-compose -f docker-compose-kafka.yml exec kafka kafka-topics --create --topic test-topic --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1
```

## Step 5: Test Producer and Consumer

You can test your Kafka setup by producing and consuming messages:

1. Produce a message:
   ```bash
   docker-compose -f docker-compose-kafka.yml exec kafka bash -c "echo 'Hello, Kafka!' | kafka-console-producer --broker-list localhost:9092 --topic test-topic"
   ```

2. Consume messages:
   ```bash
   docker-compose -f docker-compose-kafka.yml exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic test-topic --from-beginning
   ```

You should see the message "Hello, Kafka!" in the consumer output.

## Step 6: Connect Your Application

Update your Kafka consumer application to connect to the Kafka broker:

- Kafka Bootstrap Servers: `localhost:29092`
- Zookeeper connection: `localhost:22181`

## Step 7: Stopping the Containers

When you're done, you can stop the Docker containers using:

```bash
docker-compose -f docker-compose-kafka.yml down
```

## Troubleshooting

- If you can't connect to Kafka, ensure that the ports are not being used by other services on your machine.
- Check Docker logs using `docker-compose -f docker-compose-kafka.yml logs` if you encounter any issues.

## Conclusion

You now have a working Kafka setup using Docker, which you can use for development and testing. This setup includes a single Kafka broker, Zookeeper, and a user-friendly UI for managing your Kafka cluster. Remember that this setup is intended for development purposes and is not suitable for production use without further configuration and security measures.