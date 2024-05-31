import json
import random
from datetime import datetime, timedelta

import pytz

from api_helper.event_helper import APIHelper

class EventSimulator:
    def __init__(self, api_helper, systems_flow, delta, business_days, starting_date):
        self.api_helper = api_helper
        self.systems_flow = systems_flow
        self.delta = int(delta)
        self.business_days = int(business_days)
        self.starting_date = datetime.strptime(starting_date, '%Y-%m-%d').date()

    def parse_time(self, business_date, time_str):
        date_format = "%Y-%m-%d"
        time_offset = time_str.split(' + ')[1]
        hours, minutes, seconds = map(int, time_offset.split(':'))
        base_date = datetime.strptime(business_date, date_format)
        return base_date + timedelta(hours=hours, minutes=minutes, seconds=seconds)

    def apply_random_delta(self, time):
        delta_seconds = random.randint(-self.delta, self.delta)
        return time + timedelta(seconds=delta_seconds)

    def generate_event_details(self, event_type):
        if event_type == 'FILE':
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

    def run_simulation(self):
        utc = pytz.UTC

        for day in range(self.business_days):
            business_date = (self.starting_date + timedelta(days=day)).strftime('%Y-%m-%d')
            print(f"Simulating events for business date: {business_date}")
            events_queue = []

            for system in self.systems_flow['systems']:
                for event in system['events']:
                    events_queue.append((system['name'], event, business_date, 0))

            while events_queue:
                system_name, event, business_date, accumulated_delay = events_queue.pop(0)
                expected_time = self.parse_time(business_date, event['expectedTime'])
                adjusted_time = self.apply_random_delta(expected_time) + timedelta(seconds=accumulated_delay)
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
                print(f"{event['name']} at {adjusted_time} with status {event['status']}")

                if event['status'] == 'SUCCESS':
                    accumulated_delay += (adjusted_time - expected_time).total_seconds()

                # Add dependent events to the queue
                for dependent_system in self.systems_flow['systems']:
                    for dependent_event in dependent_system['events']:
                        if dependent_event.get('dependency') == event['name'] and dependent_event.get('dependencyStatus') == event['status']:
                            events_queue.append((dependent_system['name'], dependent_event, business_date, accumulated_delay))

def load_config(config_file):
    config = {}
    with open(config_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config
