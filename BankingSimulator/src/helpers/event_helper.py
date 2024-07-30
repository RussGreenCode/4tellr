import json
import logging
import requests

class EventHelper:
    def __init__(self, output_mode='console', endpoint_url=None):
        self.output_mode = output_mode
        self.endpoint_url = endpoint_url

    def generate_event_details(self, event_type, status):

        if status == 'ERROR':
            return {
                "error_code": "ERR-008",
                "error_description": "500 Server Error: INTERNAL SERVER ERROR for url: http://127.0.0.1:5000/api/events"
            }


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

    def generate_event(self, process, status, current_time, business_date):
        event = {
            "businessDate": business_date,
            "eventName": process["process_id"],
            "eventType": process["type"],
            "batchOrRealtime": "Batch",
            "eventTime": current_time.isoformat(),
            "eventStatus": status,
            "resource": "Machine_1",
            "message": "",
            "details": self.generate_event_details(process["type"], status)
        }
        return event

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
