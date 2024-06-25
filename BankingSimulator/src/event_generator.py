import json
import os
from datetime import datetime, timedelta
import time
import logging
import random
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EventGenerator:
    def __init__(self, configs, mode='real_time', output_mode='console', start_time=None, multiplier=1,
                 endpoint_url=None, start_time_variance=20, dependency_variance_min=1, dependency_variance_max=2,
                 processing_time_variance=1.0):
        self.configs = configs
        self.events = []
        self.mode = mode
        self.output_mode = output_mode
        self.endpoint_url = endpoint_url
        self.program_start_time = datetime.now()  # Initialize the program start time
        self.start_time = start_time if start_time else datetime.now()  # Initialize the start time for events
        self.multiplier = multiplier
        self.start_time_variance = start_time_variance  # Maximum start time variance in minutes for initial events
        self.dependency_variance_min = dependency_variance_min  # Minimum variance for dependent events
        self.dependency_variance_max = dependency_variance_max  # Maximum variance for dependent events
        self.processing_time_variance = processing_time_variance  # Maximum processing time variance (e.g., 1.0 for 100%)
        self.process_status = {}  # Track the status of all processes
        self.virtual_time = self.start_time  # Initialize virtual time for accelerated mode

    def generate_event(self, process, status, current_time):
        event = {
            "businessDate": process.get("businessDate", self.start_time.strftime("%Y-%m-%d")),
            "eventName": process["process_id"],
            "eventType": process["type"],
            "batchOrRealtime": "Batch",
            "eventTime": current_time.isoformat(),
            "eventStatus": status,
            "resource": "Machine_1",
            "message": "",
            "details": self.generate_event_details(process["type"])
        }
        self.events.append(event)
        self.process_status[process["process_id"]] = status
        self.output_event(event)
        logging.info(f"Generated event: {event['eventName']} with status: {status} at time: {current_time}")

    def generate_event_details(self, event_type):
        if event_type == 'PROCESS':
            return {
                "processId": "proc-12345",
                "processName": "SampleProcess"
            }
        elif event_type == 'FILE':
            return {
                "fileName": "sample.csv",
                "fileLocation": "/data/files",
                "fileSize": 1024,
                "numberOfRows": 100
            }
        elif event_type == 'MESSAGE':
            return {
                "messageId": "msg-12345",
                "messageQueue": "queue-01"
            }
        elif event_type == 'DATABASE':
            return {
                "databaseName": "test_db",
                "tableName": "test_table",
                "operation": "INSERT"
            }
        else:
            return {}

    def output_event(self, event):
        if self.output_mode == 'console':
            print(json.dumps(event, indent=2))
        elif self.output_mode == 'endpoint' and self.endpoint_url:
            try:
                response = requests.post(self.endpoint_url, json=event)
                response.raise_for_status()
                logging.info(f"Event sent to {self.endpoint_url}: {response.status_code}")
            except requests.RequestException as e:
                logging.error(f"Failed to send event to {self.endpoint_url}: {e}")

    def process_time_to_minutes(self, process_time):
        return int(process_time.split()[0])

    def randomize_start_time(self, schedule_time, has_dependencies):
        if has_dependencies:
            variance = random.randint(self.dependency_variance_min, self.dependency_variance_max)
        else:
            variance = random.randint(0, self.start_time_variance)
        return schedule_time + timedelta(minutes=variance)

    def randomize_processing_time(self, processing_time):
        variance = random.uniform(0, self.processing_time_variance)
        return processing_time * (1 + variance)

    def dependencies_met(self, process):
        for dependency in process["dependencies"]:
            if self.process_status.get(dependency) != "SUCCESS":
                return False
        return True

    def schedule_initial_processes(self):
        process_queue = []
        for config in self.configs:
            for process in config["processes"]:
                self.process_status[process["process_id"]] = "PENDING"
                if not process["dependencies"]:
                    schedule_time = datetime.strptime(f"{self.start_time.date()} {process['schedule_time']}",
                                                      "%Y-%m-%d %H:%M")
                    randomized_start_time = self.randomize_start_time(schedule_time, has_dependencies=False)
                    process_queue.append((randomized_start_time, process, "STARTED"))
                    logging.info(
                        f"Added initial process to queue: {process['process_id']} scheduled for {randomized_start_time}")
        return process_queue

    def update_virtual_time(self):
        elapsed = (datetime.now() - self.program_start_time).total_seconds()
        self.virtual_time = self.start_time + timedelta(seconds=elapsed * self.multiplier)
        return self.virtual_time

    def process_events(self, process_queue):
        next_virtual_time_print = self.virtual_time + timedelta(minutes=15)
        while process_queue:
            current_time = datetime.now() if self.mode == 'real_time' else self.update_virtual_time()
            if self.virtual_time >= next_virtual_time_print:
                logging.info(f"Virtual Time: {self.virtual_time}")
                next_virtual_time_print += timedelta(minutes=15)

            process_queue.sort(key=lambda x: x[0])
            while process_queue and current_time >= process_queue[0][0]:
                next_time, next_process, status = process_queue.pop(0)
                logging.info(
                    f"Waking up to process event: {next_process['process_id']} with status: {status} scheduled for: {next_time}")

                if status == "STARTED" and not self.dependencies_met(next_process):
                    logging.info(f"Dependencies not met for: {next_process['process_id']}. Requeuing.")
                    process_queue.append((next_time, next_process, status))
                    continue

                self.generate_event(next_process, status, current_time)

                if status == "STARTED":
                    processing_time = self.process_time_to_minutes(next_process["processing_time"])
                    randomized_processing_time = self.randomize_processing_time(processing_time)
                    end_time = next_time + timedelta(minutes=randomized_processing_time)
                    process_queue.append((end_time, next_process, "SUCCESS"))
                    logging.info(f"Scheduled end event for: {next_process['process_id']} at time: {end_time}")

                    for config in self.configs:
                        for process in config["processes"]:
                            if next_process["process_id"] in process["dependencies"] and self.dependencies_met(process):
                                dependent_start_time = self.randomize_start_time(end_time, has_dependencies=True)
                                process_queue.append((dependent_start_time, process, "STARTED"))
                                logging.info(
                                    f"Scheduled dependent process: {process['process_id']} to start at: {dependent_start_time}")
                else:
                    for config in self.configs:
                        for process in config["processes"]:
                            if next_process["process_id"] in process["dependencies"] and self.dependencies_met(process):
                                dependent_start_time = self.randomize_start_time(current_time, has_dependencies=True)
                                process_queue.append((dependent_start_time, process, "STARTED"))
                                logging.info(
                                    f"Dependencies met, scheduling process: {process['process_id']} to start at: {dependent_start_time}")

            if process_queue:
                next_time = process_queue[0][0]
                time_to_wait = (next_time - current_time).total_seconds() / self.multiplier
                if time_to_wait > 0:
                    logging.info(f"Sleeping for: {time_to_wait} seconds")
                    time.sleep(time_to_wait)

    def run(self):
        process_queue = self.schedule_initial_processes()
        self.process_events(process_queue)


def load_configs(directory):
    configs = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as file:
                config = json.load(file)
                configs.append(config)
    return configs


def load_config_txt(config_path):
    config_params = {}
    with open(config_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split('=')
            config_params[key] = value
    return config_params


if __name__ == "__main__":
    config_txt_path = "./config.txt"  # Path to the config.txt file
    config_params = load_config_txt(config_txt_path)

    mode = config_params.get('mode', 'real_time')
    start_time = datetime.fromisoformat(config_params.get('start_time'))
    multiplier = int(config_params.get('multiplier', 1))
    directory_path = config_params.get('directory_path', './configs/')
    output_mode = config_params.get('output_mode', 'console')
    endpoint_url = config_params.get('endpoint_url', 'http://127.0.0.1/api/event')
    start_time_variance = int(config_params.get('start_time_variance', 20))
    dependency_variance_min = int(config_params.get('dependency_variance_min', 1))
    dependency_variance_max = int(config_params.get('dependency_variance_max', 2))
    processing_time_variance = float(config_params.get('processing_time_variance', 1.0))

    configs = load_configs(directory_path)

    business_date = datetime.now().strftime("%Y-%m-%d")
    for config in configs:
        for process in config["processes"]:
            process["businessDate"] = business_date  # Assign business date to each process

    print(f"Processing configurations for business date: {business_date}")
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
        processing_time_variance=processing_time_variance
    )
    event_generator.run()
