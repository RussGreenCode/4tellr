from configparser import ConfigParser, NoOptionError
import os
from typing import Dict
import logging

class ConfigLoader:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, str]:
        config_parser = ConfigParser()
        config_parser.read(os.path.join(os.path.dirname(__file__), 'config.txt'))

        mongo_uri = ''
        try:
            mongo_uri = config_parser.get('DEFAULT', 'MONGO_URI')
        except NoOptionError:
            self.logger.warning("'MONGO_URI' option not found in config file. Using empty string.")

        return {
            'MONGO_URI': os.getenv('MONGO_URI', mongo_uri),
            'KAFKA_BOOTSTRAP_SERVERS': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 
                                               config_parser.get('KAFKA', 'BOOTSTRAP_SERVERS')),
            'KAFKA_TOPIC': os.getenv('KAFKA_TOPIC', config_parser.get('KAFKA', 'TOPIC')),
            'KAFKA_GROUP_ID': os.getenv('KAFKA_GROUP_ID', config_parser.get('KAFKA', 'GROUP_ID')),
            'PROMETHEUS_PUSHGATEWAY': os.getenv('PROMETHEUS_PUSHGATEWAY', 'localhost:9091'),
            'KAFKA_DLQ_TOPIC': 'trade_events_errors',
        }

    def get(self, key: str) -> str:
        return self.config.get(key, '')
