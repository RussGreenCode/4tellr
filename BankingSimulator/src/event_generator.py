import json
import os
from datetime import datetime, timedelta, timezone
import time
import logging
import random
import requests

from helpers.event_helper import EventHelper
from processing_calendar import ProcessingCalendar

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
        self.program_start_time = datetime.now(timezone.utc)  # Initialize the program start time in UTC
        self.start_time = start_time if start_time else datetime.now(
            timezone.utc)  # Initialize the start time for events in UTC
        self.multiplier = multiplier
        self.start_time_variance = start_time_variance  # Maximum start time variance in minutes for initial events
        self.dependency_variance_min = dependency_variance_min  # Minimum variance for dependent events
        self.dependency_variance_max = dependency_variance_max  # Maximum variance for dependent events
        self.processing_time_variance = processing_time_variance  # Maximum processing time variance (e.g., 1.0 for 100%)
        self.process_status = {}  # Track the status of all processes
        self.virtual_time = self.start_time  # Initialize virtual time for accelerated mode
        self.event_helper = EventHelper(output_mode=output_mode, endpoint_url=endpoint_url)
        self.calendar = ProcessingCalendar()  # Initialize the calendar

    def randomize_start_time(self, schedule_time, has_dependencies):
        if has_dependencies:
            variance = random.randint(self.dependency_variance_min, self.dependency_variance_max)
        else:
            variance = random.randint(0, self.start_time_variance)
        return schedule_time + timedelta(minutes=variance)

    def randomize_processing_time(self, processing_time):
        variance = random.uniform(0, self.processing_time_variance)
        return processing_time * (1 + variance)

    def process_time_to_minutes(self, process_time):
        return int(process_time.split()[0])

    def dependencies_met(self, process):
        for dependency in process["dependencies"]:
            if self.process_status.get(dependency) != "SUCCESS":
                return False
        return True

    def parse_schedule_time(self, business_date, schedule_time):
        parts = schedule_time.split(" ")
        if len(parts) != 2:
            raise ValueError(f"Invalid schedule_time format: {schedule_time}")

        day_part, time_part = parts
        if "T+" in day_part:
            days_to_add = int(day_part.split("+")[1])
            target_date = datetime.strptime(business_date, "%Y-%m-%d") + timedelta(days=days_to_add)
        elif day_part == "T":
            target_date = datetime.strptime(business_date, "%Y-%m-%d")
        else:
            raise ValueError(f"Invalid schedule_time day part: {day_part}")

        # Ensure time_part is correctly formatted
        if not (time_part[:2].isdigit() and time_part[3:].isdigit() and time_part[2] == ':'):
            raise ValueError(f"Invalid time part format: {time_part}")

        schedule_datetime = datetime.strptime(f"{target_date.strftime('%Y-%m-%d')} {time_part}",
                                              "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        return schedule_datetime

    def schedule_initial_processes(self, business_date):
        process_queue = []
        for config in self.configs:
            for process in config["processes"]:
                process["businessDate"] = business_date  # Assign business date to each process
                self.process_status[process["process_id"]] = "PENDING"
                if not process["dependencies"]:
                    schedule_time = self.parse_schedule_time(business_date, process['schedule_time'])
                    randomized_start_time = self.randomize_start_time(schedule_time, has_dependencies=False)
                    process_queue.append((randomized_start_time, process, "STARTED"))
                    logging.info(
                        f"Added initial process to queue: {process['process_id']} scheduled for {randomized_start_time}")
        return process_queue

    def update_virtual_time(self):
        elapsed = (datetime.now(timezone.utc) - self.program_start_time).total_seconds()
        self.virtual_time = self.start_time + timedelta(seconds=elapsed * self.multiplier)
        return self.virtual_time

    def process_events(self, process_queue, business_date):
        next_virtual_time_print = self.virtual_time + timedelta(minutes=15)
        while process_queue:
            current_time = datetime.now(timezone.utc) if self.mode == 'real_time' else self.update_virtual_time()
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

                # Ensure processing_time exists in the process
                if "processing_time" not in next_process:
                    logging.error(
                        f"Process '{next_process['process_id']}' does not have a 'processing_time' key in file {next_process['businessDate']}.")
                    continue

                # Modification: Check if a process with dependencies has a schedule_time and enforce the start after schedule_time
                if next_process.get('schedule_time') and next_process.get('dependencies'):
                    schedule_time = self.parse_schedule_time(business_date, next_process['schedule_time'])
                    if next_time < schedule_time:
                        logging.info(
                            f"Process '{next_process['process_id']}' has dependencies and schedule_time, rescheduling to after schedule_time.")
                        logging.info(f"Schedule time: {schedule_time}, Proposed start time: {next_time}")
                        next_time = self.randomize_start_time(schedule_time, has_dependencies=True)
                        logging.info(f"New start time after schedule_time override: {next_time}")
                        process_queue.append((next_time, next_process, status))
                        continue

                event = self.event_helper.generate_event(next_process, status, current_time, business_date)
                self.event_helper.output_event(event)
                self.process_status[next_process["process_id"]] = status

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

    def run_for_business_date(self, business_date):
        logging.info(f"Processing configurations for business date: {business_date}")
        self.start_time = datetime.combine(datetime.strptime(business_date, "%Y-%m-%d"),
                                           self.start_time.time()).replace(tzinfo=timezone.utc)
        self.program_start_time = datetime.now(timezone.utc)  # Reset the program start time to UTC
        self.virtual_time = self.start_time  # Reset the virtual time to UTC
        process_queue = self.schedule_initial_processes(business_date)
        self.process_events(process_queue, business_date)

    def run_real_time(self):
        while True:
            current_date = datetime.now(timezone.utc).date()
            if self.calendar.is_business_day(current_date):
                self.run_for_business_date(current_date.strftime("%Y-%m-%d"))
                while datetime.now(timezone.utc).date() == current_date:
                    time.sleep(60)  # Sleep for a minute before checking the date again
            else:
                time.sleep(3600)  # Sleep for an hour if it's not a business day

    def run(self, start_business_date=None, number_of_days=None):
        if self.mode == 'real_time':
            self.run_real_time()
        else:
            current_date = start_business_date
            days_processed = 0

            while days_processed < number_of_days:
                if self.calendar.is_business_day(current_date):
                    self.run_for_business_date(current_date.strftime("%Y-%m-%d"))
                    days_processed += 1
                current_date += timedelta(days=1)


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
    