import aiohttp
import logging
from prometheus_client import Counter, Histogram, CollectorRegistry, push_to_gateway
import asyncio

class Metrics:
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.prometheus_available = False
        self.registry = CollectorRegistry()
        self.message_counter = Counter('kafka_messages_processed', 
                                     'Number of Kafka messages processed', 
                                     registry=self.registry)
        self.message_latency = Histogram('kafka_message_latency_seconds',
                                       'Message processing latency in seconds',
                                       registry=self.registry)
        self.dlq_counter = Counter('dlq_messages',
                                 'Number of messages sent to dead-letter queue',
                                 registry=self.registry)

    async def check_prometheus_connection(self) -> None:
        pushgateway_url = f"http://{self.config.get('PROMETHEUS_PUSHGATEWAY')}"
        max_retries = 3
        retry_delay = 2

        async with aiohttp.ClientSession() as session:
            for attempt in range(max_retries):
                try:
                    async with session.get(pushgateway_url, timeout=5) as response:
                        if response.status == 200:
                            self.prometheus_available = True
                            self.logger.info("Successfully connected to Prometheus Pushgateway")
                            return
                except aiohttp.ClientError:
                    self.logger.warning(
                        f"Failed to connect to Prometheus Pushgateway (attempt {attempt + 1}/{max_retries})")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)

        self.logger.warning("Unable to connect to Prometheus Pushgateway. Metrics disabled.")

    def record_metrics(self, num_messages: int, processing_time: float) -> None:
        if self.prometheus_available:
            self.message_counter.inc(num_messages)
            self.message_latency.observe(processing_time)
            try:
                push_to_gateway(
                    self.config.get('PROMETHEUS_PUSHGATEWAY'),
                    job='kafka_consumer',
                    registry=self.registry
                )
            except Exception as e:
                self.logger.error(f"Failed to push metrics to Prometheus: {e}")

    def record_dlq_message(self) -> None:
        if self.prometheus_available:
            self.dlq_counter.inc()
            try:
                push_to_gateway(
                    self.config.get('PROMETHEUS_PUSHGATEWAY'),
                    job='kafka_consumer',
                    registry=self.registry
                )
            except Exception as e:
                self.logger.error(f"Failed to push DLQ metric to Prometheus: {e}")