import boto3
import uuid
import datetime
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

class DynamoDBHelper:
    def __init__(self, config):
        self.config = config
        if config['ENVIRONMENT'] == 'local':
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=config['LOCAL_DYNAMODB_ENDPOINT'],
                region_name=config['AWS_REGION']
            )
        else:
            self.dynamodb = boto3.resource(
                'dynamodb',
                aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'],
                region_name=config['AWS_REGION']
            )
        self.table = self.dynamodb.Table(config['DYNAMODB_TABLE'])

    def insert_event(self, event_data):
        event_id = str(uuid.uuid4())
        event_data['eventId'] = event_id
        self.table.put_item(Item=event_data)
        return event_id

    def query_events_by_date(self, business_date):
        response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('businessDate').eq(business_date)
        )
        return response['Items']

    def query_event_details(self, event_id):
        response = self.table.query(
            IndexName='StatusIndex',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('event_id').eq(event_id)
        )
        if response['Items']:
            return response['Items'][0]
        else:
            return None

def load_config(config_file):
    config = {}
    with open(config_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config
