import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
from datetime import datetime, timedelta
import statistics
import logging

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
        self.event_table = self.dynamodb.Table(config['EVENT_TABLE'])
        self.stats_table = self.dynamodb.Table(config['STATS_TABLE'])

        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def get_sla_slo_thresholds(self, event_name, event_status):
        return {
            'on_time': timedelta(minutes=10),
            'slo': timedelta(minutes=30),
            'sla': timedelta(minutes=60)
        }

    def insert_event(self, event_data):
        event_id = 'EVT#' + event_data['eventName'] + '#' + event_data['eventStatus'] + '#' + str(uuid.uuid4())
        event_data['eventId'] = event_id
        event_data['type'] = 'event'
        self.event_table.put_item(Item=event_data)

        # Create event outcome
        self.insert_event_outcome(event_data)
        return event_id

    def insert_event_outcome(self, event_data):
        business_date = event_data['businessDate']
        event_name = event_data['eventName']
        event_status = event_data['eventStatus']
        event_time = datetime.fromisoformat(event_data['timestamp'])

        # Get expectation for the event using the composite key
        response = self.event_table.query(
            KeyConditionExpression=Key('businessDate').eq(business_date) &
                                   Key('eventId').begins_with(f'EXP#{event_name}#{event_status}')
        )
        items = response['Items']

        if not items:
            self.logger.info(f'No expectation found for {event_name} with status {event_status} on {business_date}')
            expected_time = None
            delta = None
            outcome_status = 'NEW'
        else:
            # Assuming there is only one expectation per event_name, event_status, and business_date
            expectation = items[0]
            expected_time = datetime.fromisoformat(expectation['expectedArrival'])
            delta = event_time - expected_time

            # Get SLA, SLO thresholds
            thresholds = self.get_sla_slo_thresholds(event_name, event_status)
            outcome_status = 'ON_TIME' if delta <= thresholds['on_time'] else \
                'MEETS_SLO' if delta <= thresholds['slo'] else \
                    'MEETS_SLA' if delta <= thresholds['sla'] else \
                        'LATE'

        outcome_data = {
            'type': 'outcome',
            'eventId': 'OUT#' + event_data['eventName'] + '#' + event_data['eventStatus'] + '#' + str(uuid.uuid4()),
            'eventName': event_data['eventName'],
            'eventStatus': event_data['eventStatus'],
            'businessDate': event_data['businessDate'],
            'eventTime': event_time.isoformat(),
            'expectedTime': expected_time.isoformat() if expected_time else None,
            'delta': delta.total_seconds() if delta else None,
            'outcomeStatus': outcome_status
        }

        self.event_table.put_item(Item=outcome_data)
        self.logger.info(f'Inserted event outcome: {outcome_data["eventId"]}')

    def insert_event_outcome(self, event_data):
        outcome_id = 'OUT#' + event_data['eventName'] + '#' + event_data['eventStatus'] + '#' + str(uuid.uuid4())
        event_data['eventId'] = outcome_id
        event_data['type'] = 'outcome'



        self.event_table.put_item(Item=event_data)
        return outcome_id


    def query_events_by_date(self, business_date):
        response = self.event_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('businessDate').eq(business_date)
        )
        return response['Items']

    def scan_events_last_month(self):
        today = datetime.now()
        one_month_ago = today - timedelta(days=30)
        events = []

        for i in range((today - one_month_ago).days + 1):
            day = (one_month_ago + timedelta(days=i)).strftime('%Y-%m-%d')
            events.extend(self.query_events_by_date(day))

        return events

    def query_event_details(self, event_id):
        response = self.event_table.query(
            IndexName='StatusIndex',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('event_id').eq(event_id)
        )
        if response['Items']:
            return response['Items'][0]
        else:
            return None

    def calculate_expected_time(self, events):
        # Extract times and convert to datetime objects
        times = [datetime.fromisoformat(event['timestamp']).time() for event in events]

        # Calculate average time excluding outliers
        times_in_seconds = [t.hour * 3600 + t.minute * 60 + t.second for t in times]
        mean = statistics.mean(times_in_seconds)
        stdev = statistics.stdev(times_in_seconds)

        filtered_times = [t for t in times_in_seconds if abs(t - mean) < 2 * stdev]
        avg_seconds = int(statistics.mean(filtered_times))

        avg_time = datetime.min + timedelta(seconds=avg_seconds)
        return avg_time.time()

    def update_expected_times(self):
        events = self.scan_events_last_month()
        if not events:
            return None

        grouped_events = {}
        for event in events:
            key = (event['eventName'], event['eventStatus'])
            if key not in grouped_events:
                grouped_events[key] = []
            grouped_events[key].append(event)

        for (event_name, event_status), group in grouped_events.items():
            expected_time = self.calculate_expected_time(group)
            if expected_time:
                self.stats_table.put_item(
                    Item={
                        'event_name_and_status': event_name + '#' + event_status,
                        'expected_time': expected_time.isoformat(),
                        'last_updated': datetime.now().isoformat()
                    }
                )

    def get_expected_time(self, event_name, event_status):
        response = self.stats_table.get_item(
            Key={
                'eventName': event_name,
                'eventStatus': event_status
            }
        )
        return response.get('Item')


    def get_latest_metrics(self):
        # Perform a scan to get all items
        response = self.stats_table.scan()
        items = response['Items']

        # Dictionary to keep track of the latest item for each eventNameAndStatus
        latest_metrics = {}
        for item in items:
            key = item['event_name_and_status']
            if key not in latest_metrics or item['last_updated'] > latest_metrics[key]['last_updated']:
                latest_metrics[key] = item

        # Return the latest metrics as a list
        return list(latest_metrics.values())


    def generate_expectations(self, business_date):
        latest_metrics = self.get_latest_metrics()
        expectations = []

        self.logger.info(f'Found {len(latest_metrics)} metrics for {business_date}')

        for metric in latest_metrics:
            event_name, event_status = metric['event_name_and_status'].split('#')
            expected_time_str = metric['expected_time']
            expected_time = datetime.strptime(expected_time_str, "%H:%M:%S").time()

            expected_datetime = datetime.combine(datetime.strptime(business_date, "%Y-%m-%d"), expected_time)

            expectation_id = f'EXP#{event_name}#{event_status}#{str(uuid.uuid4())}'
            expectation_data = {
                'type': 'expectation',
                'eventId': expectation_id,
                'eventName': event_name,
                'eventStatus': event_status,
                'businessDate': business_date,
                'expectedArrival': expected_datetime.isoformat()
            }

            self.event_table.put_item(Item=expectation_data)
            expectations.append(expectation_data)

        self.logger.info(f'Created {len(expectations)} Expectations for {business_date}')

        return expectations

    def delete_expectations_for_business_date(self, business_date):
        try:
            # Scan to get all items with keys starting with 'EXP#' and matching the business date
            response = self.event_table.scan(
                FilterExpression=Attr('eventId').begins_with('EXP#') & Attr('businessDate').eq(business_date)
            )
            items = response['Items']
            self.logger.info(f'Found {len(items)} items to delete for business date {business_date}')

            # Delete all matching items
            with self.event_table.batch_writer() as batch:
                for item in items:
                    try:
                        batch.delete_item(
                            Key={
                                'businessDate': item['businessDate'],
                                'eventId': item['eventId']
                            }
                        )
                    except Exception as e:
                        self.logger.error(f'Error deleting item with eventId: {item["eventId"]} - {str(e)}')
                self.logger.info(f'Deleted {len(items)} items for business date {business_date}')

        except Exception as e:
            self.logger.error(f'Error scanning items for business date {business_date} - {str(e)}')
            raise

    def delete_events_for_business_date(self, business_date):
        try:
            # Scan to get all items with keys starting with 'EXP#' and matching the business date
            response = self.event_table.scan(
                FilterExpression=Attr('eventId').begins_with('EVT#') & Attr('businessDate').eq(business_date)
            )
            items = response['Items']
            self.logger.info(f'Found {len(items)} events to delete for business date {business_date}')

            # Delete all matching items
            with self.event_table.batch_writer() as batch:
                for item in items:
                    try:
                        batch.delete_item(
                            Key={
                                'businessDate': item['businessDate'],
                                'eventId': item['eventId']
                            }
                        )
                    except Exception as e:
                        self.logger.error(f'Error deleting item with eventId: {item["eventId"]} - {str(e)}')
                self.logger.info(f'Deleted {len(items)} events for business date {business_date}')

        except Exception as e:
            self.logger.error(f'Error scanning items for business date {business_date} - {str(e)}')
            raise


def load_config(config_file):
    config = {}
    with open(config_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config