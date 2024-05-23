import requests
from datetime import datetime
from api_helper.validators import ValidationError, CommonFieldValidator, FileEventValidator, MessageEventValidator, DatabaseEventValidator

class APIHelper:
    def __init__(self, api_url):
        self.api_url = api_url
        self.validators = []

    def add_validator(self, validator):
        self.validators.append(validator)

    def validate_message(self, message):
        for validator in self.validators:
            validator.validate(message)

    def create_event_payload(self, event_type, details):
        payload = {
            "businessDate": "2023-11-30",
            "eventName": f"Test Event {datetime.utcnow().isoformat()}",
            "eventType": event_type,
            "batchOrRealtime": "Batch",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "eventStatus": "Started",
            "resource": "test-machine",
            "message": "Test event message.",
            "details": details
        }
        self.validate_message(payload)
        return payload

    def call_api(self, payload):
        response = requests.post(self.api_url, json=payload)
        if response.status_code == 201:
            print(f"Event created successfully: {response.json()}")
        else:
            print(f"Failed to create event: {response.status_code} - {response.json()}")

    def send_event(self, event_type, details):
        payload = self.create_event_payload(event_type, details)
        self.call_api(payload)
