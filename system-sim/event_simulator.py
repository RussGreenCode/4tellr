import json
import random
from datetime import datetime, timedelta
import pytz

class EventSimulator:
    def __init__(self, api_helper, systems_flow, late_delta, early_delta, business_days, starting_date):
        self.api_helper = api_helper
        self.systems_flow = systems_flow
        self.late_delta = int(late_delta)
        self.early_delta = int(early_delta)
        self.business_days = int(business_days)
        self.starting_date = datetime.strptime(starting_date, '%Y-%m-%d').date()
        self.accumulated_delays = {}

    def parse_time(self, business_date, time_str):
        date_format = "%Y-%m-%d"
        time_offset = time_str.split(' + ')[1]
        hours, minutes, seconds = map(int, time_offset.split(':'))
        base_date = datetime.strptime(business_date, date_format)
        return base_date + timedelta(hours=hours, minutes=minutes, seconds=seconds)

    def apply_random_delta(self):
        if random.choice([True, False]):
            delta_seconds = random.randint(0, self.early_delta) * -1  # Only negative for early
        else:
            delta_seconds = random.randint(0, self.late_delta)  # Only positive for late
        return delta_seconds

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
    def log_delay(self, system_name, event_name, delay):
        key = f"{system_name}:{event_name}"
        if key not in self.accumulated_delays:
            self.accumulated_delays[key] = []
        self.accumulated_delays[key].append(delay)
        print(f"Logged delay for {key}: {delay} seconds (Total delays: {self.accumulated_delays[key]})")

    def run_simulation(self):
        utc = pytz.UTC

        for day in range(self.business_days):
            business_date = (self.starting_date + timedelta(days=day)).strftime('%Y-%m-%d')
            print(f"Simulating events for business date: {business_date}")
            events_queue = []

            for system in self.systems_flow['systems']:
                for event in system['events']:
                    if not event.get('dependency'):
                        events_queue.append((system['name'], event, business_date, 0))

            while events_queue:
                system_name, event, business_date, accumulated_delay = events_queue.pop(0)
                expected_time = self.parse_time(business_date, event['expectedTime'])
                adjusted_time = expected_time + timedelta(seconds=accumulated_delay)
                details = self.generate_event_details(event['eventType'])
                payload = {
                    "businessDate": business_date,
                    "eventName": event['name'],
                    "eventType": event['eventType'],
                    "batchOrRealtime": "Batch",
                    "eventTime": adjusted_time.astimezone(utc).isoformat(),
                    "eventStatus": event['status'],
                    "resource": "test-machine",
                    "message": "Test event message.",
                    "details": details
                }
                self.api_helper.send_event(event['eventType'], payload)
                print(f"{event['name']} at {adjusted_time} with status {event['status']} and accumulated delay {accumulated_delay}")

                if event['status'] == 'SUCCESS':
                    delta = self.apply_random_delta()
                    accumulated_delay += delta
                    self.log_delay(system_name, event['name'], accumulated_delay)

                    # Add direct dependent events to the queue
                    for dependent_system in self.systems_flow['systems']:
                        if event['name'] in dependent_system.get('dependencies', []):
                            for dependent_event in dependent_system['events']:
                                if dependent_event.get('dependency') == event['name'] and dependent_event.get('dependencyStatus') == event['status']:
                                    print(f"Adding dependent event {dependent_event['name']} from {dependent_system['name']} to the queue")
                                    events_queue.append((dependent_system['name'], dependent_event, business_date, accumulated_delay))

def load_config(config_file):
    config = {}
    with open(config_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config
