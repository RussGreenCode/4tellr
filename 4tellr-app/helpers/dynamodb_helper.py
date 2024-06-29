import boto3
import pytz
from boto3.dynamodb.conditions import Key, Attr
import uuid
from datetime import datetime, timedelta, timezone
import statistics
import logging
from dateutil import parser
import bcrypt

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
        self.monitoring_groups_table = self.dynamodb.Table(config['MONITORING_GROUPS_TABLE'])
        self.user_table = self.dynamodb.Table(config['USER_TABLE'])

        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def get_sla_slo_thresholds(self, event_name, event_status):
        return {
            'on_time': timedelta(minutes=10),
            'slo': timedelta(minutes=30),
            'sla': timedelta(minutes=60)
        }

    def get_plot_status(self, plot_type, outcome_status):

        if outcome_status == 'ON_TIME':
            return 'MET_THRESHOLD'
        elif outcome_status == 'MEETS_SLO':
            if plot_type == 'EXP':
                return 'BREACHED'
            else:
                return 'MET_THRESHOLD'
        elif outcome_status == 'MEETS_SLA':
            if plot_type == 'SLA':
                return 'MET_THRESHOLD'
            else:
                return 'BREACHED'
        else:
            return 'BREACHED'


    def insert_event(self, event_data):
        event_id = 'EVT#' + event_data['eventName'] + '#' + event_data['eventStatus'] + '#' + str(uuid.uuid4())
        event_data['eventId'] = event_id
        event_data['type'] = 'event'
        event_data['timestamp'] = datetime.now(timezone.utc).isoformat()
        self.event_table.put_item(Item=event_data)
        event_time = datetime.fromisoformat(event_data['eventTime'])
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)  # Assuming UTC if not specified
            event_data['eventTime'] = event_time.isoformat()

        # Create event outcome
        self.insert_event_outcome(event_data)
        return event_id

    def insert_event_outcome(self, event_data):
        business_date = event_data['businessDate']
        event_name = event_data['eventName']
        event_status = event_data['eventStatus']
        event_time = datetime.fromisoformat(event_data['eventTime'])

        # Get expectation for the event using the composite key
        response = self.event_table.query(
            KeyConditionExpression=Key('businessDate').eq(business_date) &
                                   Key('eventId').begins_with(f'EXP#{event_name}#{event_status}')
        )
        items = response['Items']

        if not items:
            self.logger.info(f'No expectation found for {event_name} with status {event_status} on {business_date}')
            expected_time = None
            str_delta = ''
            outcome_status = 'NEW'
            slo_time = None
            sla_time = None
        else:
            # Assuming there is only one expectation per event_name, event_status, and business_date
            expectation = items[0]
            expected_time = datetime.fromisoformat(expectation['expectedArrival'])
            if expected_time.tzinfo is None:
                expected_time = expected_time.replace(tzinfo=timezone.utc)  # Assuming UTC if not specified

            delta = event_time - expected_time

            # Get SLA, SLO thresholds
            thresholds = self.get_sla_slo_thresholds(event_name, event_status)
            slo_time = (expected_time + thresholds['slo']).isoformat()
            sla_time = (expected_time + thresholds['sla']).isoformat()

            outcome_status = 'ON_TIME' if delta <= thresholds['on_time'] else \
                'MEETS_SLO' if delta <= thresholds['slo'] else \
                    'MEETS_SLA' if delta <= thresholds['sla'] else \
                        'LATE'
            str_delta = str(delta.total_seconds())

        outcome_data = {
            'type': 'outcome',
            'eventId': 'OUT#' + event_data['eventName'] + '#' + event_data['eventStatus'] + '#' + str(uuid.uuid4()),
            'eventName': event_data['eventName'],
            'eventStatus': event_data['eventStatus'],
            'businessDate': event_data['businessDate'],
            'eventTime': event_time.isoformat(),
            'expectedTime': expected_time.isoformat() if expected_time else None,
            'sloTime': slo_time,
            'slaTime': sla_time,
            'delta':  str_delta if str_delta else None,
            'outcomeStatus': outcome_status,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        self.event_table.put_item(Item=outcome_data)
        self.logger.info(f'Inserted event outcome: {outcome_data["eventId"]}')


    def query_events_by_date(self, business_date):
        response = self.event_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('businessDate').eq(business_date)
        )
        return response['Items']

    def query_events_by_date_for_chart(self, business_date):
        response = self.event_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('businessDate').eq(business_date)
        )

        items = response['Items']
        result = []
        utc = pytz.UTC

        # Sort the items to process outcomes first
        items.sort(key=lambda x: x['eventId'].startswith('OUT#'), reverse=True)

        processed_event_keys = set()

        current_time = datetime.now(timezone.utc)

        for item in items:
            event_id = item.get('eventId')
            type_of_event = item.get('type')
            event_type = item.get('eventType')
            event_name = item.get('eventName')
            event_status = item.get('eventStatus')
            event_key = event_name + '#' + event_status
            outcome_status = item.get('outcomeStatus', 'N/A')

            if type_of_event == 'outcome':
                slo_time = item.get('sloTime')
                sla_time = item.get('slaTime')
                event_time = item.get('eventTime')
                expected_arrival = item.get('expectedTime')

                if slo_time:
                    result.append({
                        'eventId': event_id,
                        'eventType': event_type,
                        'type': 'SLO',
                        'eventName': event_name,
                        'eventKey': event_key,
                        'eventStatus': event_status,
                        'TimeValue': slo_time,
                        'outcomeStatus': outcome_status,
                        'plotStatus': self.get_plot_status("SLO", outcome_status)
                    })

                if sla_time:
                    result.append({
                        'eventId': event_id,
                        'eventType': event_type,
                        'type': 'SLA',
                        'eventName': event_name,
                        'eventKey': event_key,
                        'eventStatus': event_status,
                        'TimeValue': sla_time,
                        'outcomeStatus': outcome_status,
                        'plotStatus': self.get_plot_status("SLA", outcome_status)
                    })

                if event_time:
                    result.append({
                        'eventId': event_id,
                        'eventType': event_type,
                        'type': 'EVT',
                        'eventKey': event_key,
                        'eventName': event_name,
                        'eventStatus': event_status,
                        'TimeValue': event_time,
                        'outcomeStatus': outcome_status,
                        'plotStatus': outcome_status
                    })

                if expected_arrival:
                    result.append({
                        'eventId': event_id,
                        'eventType': event_type,
                        'type': 'EXP',
                        'eventKey': event_key,
                        'eventName': event_name,
                        'eventStatus': event_status,
                        'TimeValue': expected_arrival,
                        'outcomeStatus': outcome_status,
                        'plotStatus': outcome_status
                    })

                processed_event_keys.add(event_key)

        # Process the remaining items
        for item in items:
            event_id = item.get('eventId')
            event_type = item.get('eventType')
            event_name = item.get('eventName')
            event_status = item.get('eventStatus')
            event_key = event_name + '#' + event_status



            if event_id.startswith('EXP#') and event_key not in processed_event_keys:

                time_value = item.get('expectedArrival')
                expected_time=datetime.fromisoformat(time_value).astimezone(utc)
                thresholds = self.get_sla_slo_thresholds(event_name, event_status)

                if current_time < (expected_time + thresholds['on_time']):
                    expectation_outcome = 'NOT_REACHED'
                else:
                    expectation_outcome = 'BREACHED'

                if time_value:
                    result.append({
                        'eventId': event_id,
                        'eventType': event_type,
                        'type': 'EXP',
                        'eventKey': event_key,
                        'eventName': event_name,
                        'eventStatus': event_status,
                        'TimeValue': time_value,
                        'outcomeStatus': 'NO_EVT_YET',
                        'plotStatus': expectation_outcome
                    })
            elif event_id.startswith('EVT#') and event_key not in processed_event_keys:
                time_value = item.get('eventTime')
                if time_value:
                    result.append({
                        'eventId': event_id,
                        'eventType': event_type,
                        'type': 'EVT',
                        'eventKey': event_key,
                        'eventName': event_name,
                        'eventStatus': event_status,
                        'TimeValue': time_value,
                        'outcomeStatus': 'NEW_EVT',
                        'plotStatus': 'NEW_EVT'
                    })


        return result

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
        utc = pytz.UTC

        debug = False

        times_in_seconds = []
        for event in events:
            event_time = datetime.fromisoformat(event['eventTime']).astimezone(utc)
            business_date_utc = datetime.strptime(event['businessDate'], "%Y-%m-%d").replace(tzinfo=utc)

            if event['eventName'] == 'Fortress_MarketData_Receipt':
                self.logger.info(f"event_time: {event_time}  business_date_utc: {business_date_utc}")
                debug = True

            # Calculate the total seconds from the start of the business date to the event time
            time_difference = (event_time - business_date_utc).total_seconds()
            times_in_seconds.append(time_difference)


        # Calculate average time excluding outliers
        mean = statistics.mean(times_in_seconds)
        stdev = statistics.stdev(times_in_seconds)

        if debug:
            self.logger.info(f"Mean time in seconds: {mean}")
            self.logger.info(f"Standard deviation: {stdev}")

        filtered_times = [t for t in times_in_seconds if abs(t - mean) < 2 * stdev]
        if filtered_times and len(filtered_times) > 1:
            avg_seconds = int(statistics.mean(filtered_times))
        else:
            avg_seconds = int(mean)

        if debug:
            self.logger.info(f"Average time in seconds after filtering: {avg_seconds}")

        avg_time_delta = timedelta(seconds=avg_seconds)

        # Calculate days, hours, minutes, and seconds from the avg_time_delta
        total_hours = avg_time_delta.days * 24 + avg_time_delta.seconds // 3600
        minutes, seconds = divmod(avg_time_delta.seconds % 3600, 60)

        # Format the time as total hours, minutes, and seconds
        avg_time_elapsed = f"{total_hours:02}:{minutes:02}:{seconds:02}"

        if debug:
            self.logger.info(f"Average time elapsed: {avg_time_elapsed}")

        return avg_time_elapsed

    def update_expected_times(self):
        events = self.scan_events_last_month()
        if not events:
            return None

        grouped_events = {}
        for event in events:
            if event['type'] == 'event':
                key = (event['eventName'], event['eventStatus'])
                if key not in grouped_events:
                    grouped_events[key] = []
                grouped_events[key].append(event)

        for (event_name, event_status), group in grouped_events.items():
            try:
                avg_time_elapsed = self.calculate_expected_time(group)
                self.logger.info(f'Storing {event_name}#{event_status} for time after T +: {avg_time_elapsed}')
                if avg_time_elapsed:

                    self.stats_table.put_item(
                        Item={
                            'event_name_and_status': event_name + '#' + event_status,
                            'expected_time': avg_time_elapsed,
                            'last_updated': datetime.now().isoformat()
                        }
                    )
            except ValueError as e:
                self.logger.error(f'Failed to update expected times for {event_name}#{event_status}: {e}')

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
            delay_str = metric['expected_time']  # Now the delay in HH:MM:SS format

            try:
                # Parse the delay string to a timedelta
                hours, minutes, seconds = map(int, delay_str.split(':'))
                delay_timedelta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except ValueError as e:
                # Log the error and the problematic string
                print(f"Error parsing delay from '{delay_str}': {e}")
                continue  # Skip this iteration and proceed with the next metric

            # Combine the business_date and delay_timedelta to get the expected datetime in UTC
            business_date_dt = datetime.strptime(business_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            expected_datetime = business_date_dt + delay_timedelta

            expectation_id = f'EXP#{event_name}#{event_status}#{str(uuid.uuid4())}'
            expectation_data = {
                'type': 'expectation',
                'eventId': expectation_id,
                'eventName': event_name,
                'eventStatus': event_status,
                'businessDate': business_date,
                'expectedArrival': expected_datetime.isoformat(),
                'timestamp': datetime.now(timezone.utc).isoformat()
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

    def delete_events_for_business_dates(self, business_dates):
        for business_date in business_dates:
            try:
                # Scan to get all items with keys starting with 'EVT#' or 'OUT#' and matching the business date
                response = self.event_table.scan(
                    FilterExpression=(
                        (Attr('eventId').begins_with('EVT#') | Attr('eventId').begins_with('OUT#')) &
                        Attr('businessDate').eq(business_date)
                    )
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


    def get_monthly_events(self, event_name, event_status):

        # Calculate the start date (one month ago from today)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        # Convert dates to string format if required
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        # Query parameters
        sk_prefix = f'OUT#{event_name}#{event_status}'

        # Perform the query for each day in the date range
        all_events = []
        current_date = start_date
        while current_date <= end_date:
            current_date_str = current_date.strftime('%Y-%m-%d')
            response = self.event_table.query(
                KeyConditionExpression=Key('businessDate').eq(current_date_str) & Key('eventId').begins_with(sk_prefix)
            )
            all_events.extend(response.get('Items', []))
            current_date += timedelta(days=1)


        return {
            "events": all_events
        }

    def get_expectation_list(self):
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

    def save_group(self, group_name, events, description):
        if group_name and events is not None:
            try:
                response = self.monitoring_groups_table.put_item(
                    Item={
                        'group_name': group_name,
                        'description': description,
                        'events': events
                    }
                )
                print(f"[INFO] Group '{group_name}' saved successfully.")
                return response
            except Exception as e:
                print(f"[ERROR] Error saving group '{group_name}': {str(e)}")
                return None
        else:
            print("[ERROR] 'group_name' and 'events' must not be None.")
            return None

    def update_group(self, group_name, new_events):
        if group_name and new_events is not None:
            try:
                response = self.monitoring_groups_table.update_item(
                    Key={
                        'group_name': group_name
                    },
                    UpdateExpression="SET event_key = :e",
                    ExpressionAttributeValues={
                        ':e': new_events
                    },
                    ReturnValues="UPDATED_NEW"
                )
                print(f"[INFO] Group '{group_name}' updated successfully.")
                return response
            except Exception as e:
                print(f"[ERROR] Error updating group '{group_name}': {str(e)}")
                return None
        else:
            print("[ERROR] 'group_name' and 'new_events' must not be None.")
            return None


    def delete_group(self, group_name):
        if group_name:
            try:
                response = self.monitoring_groups_table.delete_item(
                    Key={'group_name': group_name}
                )
                print(f"[INFO] Group '{group_name}' deleted successfully.")
                return response
            except Exception as e:
                print(f"[ERROR] Error deleting group '{group_name}': {str(e)}")
                return None
        else:
            print("[ERROR] 'group_name' must not be None.")
            return None

    def get_all_groups(self):
        try:
            response = self.monitoring_groups_table.scan(
                ProjectionExpression="group_name, description"
            )
            groups = [{'group_name': item['group_name'], 'description': item.get('description', '')} for item in
                      response.get('Items', [])]
            print(f"[INFO] Retrieved {len(groups)} groups.")
            return groups
        except Exception as e:
            print(f"[ERROR] Error retrieving groups: {str(e)}")
            return None

    def get_group_details(self, group_name):
        if group_name is not None:
            try:
                response = self.monitoring_groups_table.get_item(
                    Key={
                        'group_name': group_name
                    }
                )
                if 'Item' in response:
                    group = response['Item']
                    print(f"[INFO] group '{group_name}' retrieved successfully.")
                    return group
                else:
                    print(f"[INFO] No group found for group '{group_name}'.")
                    return None
            except Exception as e:
                print(f"[ERROR] Error retrieving group '{group_name}': {str(e)}")
                return None
        else:
            print("[ERROR] 'group_name' must not be None.")
            return None

    def add_user(self, user):
        email = user.get('email')

        if not email:
            return {'error': 'Email is required'}

        try:
            # Check if the user already exists
            response = self.user_table.get_item(Key={'email': email})

            if 'Item' in response:
                return {'email': email,'success': False, 'message': 'User with this email already exists'}

            # Add the new user
            self.user_table.put_item(Item=user)
            return {'email': email, 'success': True, 'message': 'User added successfully'}

        except Exception as e:
            return {'email': email, 'success': False, 'error': str(e)}

    def delete_user_by_email(self, email):

        try:
            self.user_table.delete_item(Key={'email': email})
        except Exception as e:
            return False

        return True

    def get_all_users(self):
        try:
            response = self.user_table.scan(
                ProjectionExpression="email"
            )
            users = [{'email': item['email']} for item in
                      response.get('Items', [])]
            print(f"[INFO] Retrieved {len(users)} users.")
            return users
        except Exception as e:
            print(f"[ERROR] Error retrieving users: {str(e)}")
            return None

    def get_user_by_email(self, email):
        try:
            response = self.user_table.get_item(Key={'email': email})
            return response.get('Item', None)
        except NoCredentialsError:
            print("Credentials not available.")
            return None
        except PartialCredentialsError:
            print("Incomplete credentials provided.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def validate_user(self, email, password):
        user = self.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
        return None

    def change_password(self, email, old_password, new_password):
        user = self.get_user_by_email(email)
        if user and bcrypt.checkpw(old_password.encode('utf-8'), user['password'].encode('utf-8')):
            new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            try:
                self.user_table.update_item(
                    Key={'email': email},
                    UpdateExpression="SET password = :p",
                    ExpressionAttributeValues={':p': new_hashed_password}
                )
                return {'success': True, 'message': 'Password updated successfully'}
            except Exception as e:
                return {'success': False, 'message': str(e)}
        return {'success': False, 'message': 'Old password is incorrect'}

    def save_user_favourite_groups(self, email, favourite_groups):
        self.user_table.update_item(
            Key={'email': email},
            UpdateExpression="SET favourite_groups = :g",
            ExpressionAttributeValues={':g': favourite_groups}
        )


def load_config(config_file):
    config = {}
    with open(config_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config
