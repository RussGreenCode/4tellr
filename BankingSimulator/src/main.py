import logging
from datetime import datetime, timezone
from event_generator import EventGenerator, load_configs, load_config_txt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    config_txt_path = "./config.txt"  # Path to the config.txt file
    config_params = load_config_txt(config_txt_path)

    mode = config_params.get('mode', 'real_time')
    start_time = datetime.fromisoformat(config_params.get('start_time')).replace(tzinfo=timezone.utc)
    multiplier = int(config_params.get('multiplier', 1))
    directory_path = config_params.get('directory_path', './configs/')
    output_mode = config_params.get('output_mode', 'console')
    endpoint_url = config_params.get('endpoint_url', 'http://127.0.0.1/api/event')
    start_time_variance = int(config_params.get('start_time_variance', 20))
    dependency_variance_min = int(config_params.get('dependency_variance_min', 1))
    dependency_variance_max = int(config_params.get('dependency_variance_max', 2))
    processing_time_variance = float(config_params.get('processing_time_variance', 1.0))
    error_chance = float(config_params.get('error_chance', 1.0))  # Default error chance is 1%
    retry_delay = int(config_params.get('retry_delay', 20))  # Default retry delay is 20 minutes
    start_business_date = datetime.strptime(config_params.get('start_business_date'), "%Y-%m-%d")
    number_of_days = int(config_params.get('number_of_days', 1))

    configs = load_configs(directory_path)

    event_generator = EventGenerator(
        configs,
        mode=mode,
        output_mode=output_mode,
        start_time=start_time,
        multiplier=multiplier,
        endpoint_url=endpoint_url,
        start_time_variance=start_time_variance,
        dependency_variance_min=dependency_variance_min,
        dependency_variance_max=dependency_variance_max,
        processing_time_variance=processing_time_variance,
        error_chance=error_chance,
        retry_delay=retry_delay
    )
    event_generator.run(start_business_date, number_of_days)
