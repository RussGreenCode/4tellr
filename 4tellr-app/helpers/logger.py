# helpers/logger.py
import logging

class Logger:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        log_level = config.get('LOG_LEVEL', 'INFO').upper()
        numeric_level = getattr(logging, log_level, logging.INFO)
        self.logger.setLevel(numeric_level)

        # Create console handler and set level
        ch = logging.StreamHandler()
        ch.setLevel(numeric_level)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add formatter to ch
        ch.setFormatter(formatter)

        # Add ch to logger
        self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger
