import unittest
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import uuid
import datetime


class TestDynamoDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load configuration
        cls.config = cls.load_config('config.txt')

        if cls.config['ENVIRONMENT'] == 'local':
            cls.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=cls.config['LOCAL_DYNAMODB_ENDPOINT'],
                region_name=cls.config['AWS_REGION']
            )
        else:
            cls.dynamodb = boto3.resource(
                'dynamodb',
                aws_access_key_id=cls.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=cls.config['AWS_SECRET_ACCESS_KEY'],
                region_name=cls.config['AWS_REGION']
            )

        cls.table = cls.dynamodb.Table(cls.config['DYNAMODB_TABLE'])

    @staticmethod
    def load_config(config_file):
        config = {}
        with open(config_file, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
        return config

    def test_insert_simple_event(self):
        # Define a simple event data
        simple_event = {
            'businessDate': '2024-05-24',
            'eventName': 'TEST_EVENT',
            'eventType': 'FILE',
            'batchOrRealtime': 'Batch',
            'timestamp': '2024-05-24T12:32:51.572843Z',
            'eventStatus': 'STARTED',
            'resource': 'test-machine',
            'message': 'This is a test event',
            'eventId': str(uuid.uuid4()),  # Generate a unique event_id
            'details_fileName': 'test_file.csv',
            'details_fileLocation': '/test/location',
            'details_fileSize': 12345,
            'details_numberOfRows': 10
        }

        # Attempt to insert the event
        try:
            response = self.table.put_item(Item=simple_event)
            print(f"Insert response: {response}")
            self.assertEqual(response['ResponseMetadata']['HTTPStatusCode'], 200,
                             "Insert operation should return status code 200")
        except (NoCredentialsError, PartialCredentialsError) as e:
            self.fail(f"Insert event failed with exception: {e}")


if __name__ == '__main__':
    unittest.main()
