import boto3
import pytz
from boto3.dynamodb.conditions import Key, Attr
import uuid
from datetime import datetime, timedelta, timezone
import statistics
import bcrypt

from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from helpers.database_helper_interface import DatabaseHelperInterface
from utils.threshold import Threshold
from utils.status_utilities import StatusUtilities


class DynamoDBHelper(DatabaseHelperInterface):
    def __init__(self, config, logger):
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
        self.logger = logger


    def insert_event(self, event_data):

        try:
            self.event_table.put_item(Item=event_data)
            return True

        except Exception as e:
            print(f"[ERROR] Error storing the event: {str(e)}")
            return False


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


    def store_statistic(self, event_name, event_status, avg_time_elapsed):
        try:
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

    def delete_expectations_for_business_date(self, business_date):
        try:
            # Scan to get all items with keys starting with 'EXP#' and matching the business date

            items = self.get_event_by_starting_prefix('EXP#', business_date)

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
                # Scan to get all items matching the business date
                response = self.event_table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('businessDate').eq(business_date)
                )
                items = response['Items']
                self.logger.info(f'Found {len(items)} events for business date {business_date}')

                # Filter out items with type "event" or "outcome"
                items_to_delete = [item for item in items if item.get('type') in ['event', 'outcome']]
                self.logger.info(f'Found {len(items_to_delete)} events to delete for business date {business_date}')

                # Delete all matching items
                with self.event_table.batch_writer() as batch:
                    for item in items_to_delete:
                        try:
                            batch.delete_item(
                                Key={
                                    'businessDate': item['businessDate'],
                                    'eventId': item['eventId']
                                }
                            )
                        except Exception as e:
                            self.logger.error(f'Error deleting item with eventId: {item["eventId"]} - {str(e)}')
                    self.logger.info(f'Deleted {len(items_to_delete)} events for business date {business_date}')

            except Exception as e:
                self.logger.error(f'Error scanning items for business date {business_date} - {str(e)}')
                raise

    def get_event_by_starting_prefix(self, sk_prefix, current_date_str):

       try:
            response = self.event_table.query(
                KeyConditionExpression=Key('businessDate').eq(current_date_str) & Key('eventId').begins_with(sk_prefix)
            )

            return response.get('Items', [])

       except Exception as e:
           print(f"[ERROR] Error getting events for date: {str(e)}")
           return None


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

    # Refactored
    def add_user(self, user):
        email = user.get('email')

        try:
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

    # Refactored
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

    def change_user_password(self, email, new_hashed_password):

        try:
            self.user_table.update_item(
                Key={'email': email},
                UpdateExpression="SET password = :p",
                ExpressionAttributeValues={':p': new_hashed_password}
            )
            return {'success': True, 'message': 'Password updated successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}


    def save_user_favourite_groups(self, email, favourite_groups):
        try:
            self.user_table.update_item(
                Key={'email': email},
                UpdateExpression="SET favourite_groups = :g",
                ExpressionAttributeValues={':g': favourite_groups}
            )
            return {'success': True, 'message': 'Favourite Groups updated successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

