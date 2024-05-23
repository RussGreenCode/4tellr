import random
from api_helper.event_helper import APIHelper
from api_helper.validators import CommonFieldValidator, FileEventValidator, MessageEventValidator, \
    DatabaseEventValidator

API_URL = "http://127.0.0.1:5000/api/events"


def main():
    api_helper = APIHelper(API_URL)

    # Add validators
    api_helper.add_validator(CommonFieldValidator())
    api_helper.add_validator(FileEventValidator())
    api_helper.add_validator(MessageEventValidator())
    api_helper.add_validator(DatabaseEventValidator())

    # Example details for different event types
    file_details = {
        "fileName": "testfile.csv",
        "fileLocation": "/tmp/",
        "fileSize": 1024,
        "numberOfRows": 100
    }

    message_details = {
        "messageId": "msg-12345",
        "messageQueue": "queue-01"
    }

    database_details = {
        "databaseName": "test_db",
        "tableName": "test_table",
        "operation": "INSERT"
    }

    # Send events
    for i in range(10):
        event_type = random.choice(["File", "Message", "Database"])
        if event_type == "File":
            api_helper.send_event(event_type, file_details)
        elif event_type == "Message":
            api_helper.send_event(event_type, message_details)
        elif event_type == "Database":
            api_helper.send_event(event_type, database_details)


if __name__ == "__main__":
    main()
