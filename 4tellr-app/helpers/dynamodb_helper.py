import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
import bcrypt
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from helpers.database_helper_interface import DatabaseHelperInterface


class DynamoDBHelper(DatabaseHelperInterface):
    def __init__(self, config, logger):
        self.config = config
        self.dynamodb = self._initialize_dynamodb(config)
        self.event_table = self.dynamodb.Table(config['EVENT_TABLE'])
        self.stats_table = self.dynamodb.Table(config['STATS_TABLE'])
        self.monitoring_groups_table = self.dynamodb.Table(config['MONITORING_GROUPS_TABLE'])
        self.user_table = self.dynamodb.Table(config['USER_TABLE'])

        # Set up logging
        self.logger = logger

    def _initialize_dynamodb(self, config):
        try:
            if config['ENVIRONMENT'] == 'local':
                return boto3.resource(
                    'dynamodb',
                    endpoint_url=config['LOCAL_DYNAMODB_ENDPOINT'],
                    region_name=config['AWS_REGION']
                )
            else:
                return boto3.resource(
                    'dynamodb',
                    aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'],
                    region_name=config['AWS_REGION']
                )
        except NoCredentialsError as e:
            self.logger.error("No AWS credentials available.")
            raise e
        except PartialCredentialsError as e:
            self.logger.error("Incomplete AWS credentials.")
            raise e
        except Exception as e:
            self.logger.error(f"Error initializing DynamoDB: {e}")
            raise e

    def insert_event(self, event_data):

        try:
            self.event_table.put_item(Item=event_data)
            self.logger.info(f"Inserted event: {event_data['eventId']}")
            return {'success': True, 'message': 'Event inserted successfully'}
        except Exception as e:
            self.logger.error(f"Error storing the event: {e}")
            return {'success': False, 'error': str(e)}


    def query_events_by_date(self, business_date):
        try:
            response = self.event_table.query(
                KeyConditionExpression=Key('businessDate').eq(business_date)
            )
            return {'success': True, 'data': response['Items']}
        except Exception as e:
            self.logger.error(f"Error querying events by date: {e}")
            return {'success': False, 'error': str(e)}

    def scan_events_last_month(self):
        try:
            today = datetime.now()
            one_month_ago = today - timedelta(days=30)
            events = []

            for i in range((today - one_month_ago).days + 1):
                day = (one_month_ago + timedelta(days=i)).strftime('%Y-%m-%d')
                result = self.query_events_by_date(day)
                if result['success']:
                    events.extend(result['data'])

            return {'success': True, 'data': events}
        except Exception as e:
            self.logger.error(f"Error scanning events for the last month: {e}")
            return {'success': False, 'error': str(e)}

    def query_event_details(self, event_id):
        try:
            response = self.event_table.query(
                IndexName='StatusIndex',
                KeyConditionExpression=Key('event_id').eq(event_id)
            )
            if response['Items']:
                return {'success': True, 'data': response['Items'][0]}
            else:
                return {'success': False, 'message': 'Event not found'}
        except Exception as e:
            self.logger.error(f"Error querying event details: {e}")
            return {'success': False, 'error': str(e)}


    def store_statistic(self, event_name, event_status, avg_time_elapsed):
        try:
            self.stats_table.put_item(
                Item={
                    'event_name_and_status': event_name + '#' + event_status,
                    'expected_time': avg_time_elapsed,
                    'last_updated': datetime.now().isoformat()
                }
            )
            self.logger.info(f"Stored statistic for {event_name}#{event_status}")
            return {'success': True, 'message': 'Statistic stored successfully'}
        except Exception as e:
            self.logger.error(f"Failed to store statistic for {event_name}#{event_status}: {e}")
            return {'success': False, 'error': str(e)}

    def get_expected_time(self, event_name, event_status):
        try:
            response = self.stats_table.get_item(
                Key={
                    'eventName': event_name,
                    'eventStatus': event_status
                }
            )
            return {'success': True, 'data': response.get('Item')}
        except Exception as e:
            self.logger.error(f"Error getting expected time: {e}")
            return {'success': False, 'error': str(e)}

    def get_latest_metrics(self):
        # Perform a scan to get all items
        try:
            response = self.stats_table.scan()
            items = response['Items']
            latest_metrics = {item['event_name_and_status']: item for item in items}
            return {'success': True, 'data': list(latest_metrics.values())}
        except Exception as e:
            self.logger.error(f"Error getting latest metrics: {e}")
            return {'success': False, 'error': str(e)}

    def delete_expectations_for_business_date(self, business_date):
        try:
            exp_result  = self.get_event_by_starting_prefix('EXP#', business_date)
            items = exp_result['data']
            if items is None:
                return {'success': False, 'error': 'Error getting events for deletion'}

            with self.event_table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(Key={'businessDate': item['businessDate'], 'eventId': item['eventId']})
            self.logger.info(f"Deleted {len(items)} expectations for business date {business_date}")
            return {'success': True, 'message': f"Deleted {len(items)} expectations"}
        except Exception as e:
            self.logger.error(f"Error deleting expectations for business date {business_date}: {e}")
            return {'success': False, 'error': str(e)}

    def delete_events_for_business_dates(self, business_dates):
        try:
            for business_date in business_dates:
                response = self.event_table.query(
                    KeyConditionExpression=Key('businessDate').eq(business_date)
                )
                items = response['Items']
                items_to_delete = [item for item in items if item.get('type') in ['event', 'outcome']]

                with self.event_table.batch_writer() as batch:
                    for item in items_to_delete:
                        batch.delete_item(Key={'businessDate': item['businessDate'], 'eventId': item['eventId']})
                self.logger.info(f"Deleted {len(items_to_delete)} events for business date {business_date}")
            return {'success': True, 'message': 'Events deleted successfully'}
        except Exception as e:
            self.logger.error(f"Error deleting events for business dates: {e}")
            return {'success': False, 'error': str(e)}


    def get_event_by_starting_prefix(self, sk_prefix, current_date_str):
        try:
            response = self.event_table.query(
                KeyConditionExpression=Key('businessDate').eq(current_date_str) & Key('eventId').begins_with(sk_prefix)
            )
            events = response['Items']
            self.logger.info(f"Retrieved {len(events)} events.")
            return {'success': True, 'data': events}
        except Exception as e:
            self.logger.error(f"Error retrieving events: {str(e)}")
            return {'success': False, 'error': str(e)}


    def get_expectation_list(self):
        try:
            response = self.stats_table.scan()
            items = response['Items']
            latest_metrics = {item['event_name_and_status']: item for item in items}
            return {'success': True, 'data': list(latest_metrics.values())}
        except Exception as e:
            self.logger.error(f"Error getting expectation list: {e}")
            return {'success': False, 'error': str(e)}

    def save_group(self, group_name, events, description):
        try:
            self.monitoring_groups_table.put_item(
                Item={'group_name': group_name, 'description': description, 'events': events}
            )
            self.logger.info(f"Saved group '{group_name}' successfully")
            return {'success': True, 'message': 'Group saved successfully'}
        except Exception as e:
            self.logger.error(f"Error saving group '{group_name}': {e}")
            return {'success': False, 'error': str(e)}

    def update_group(self, group_name, new_events):
        try:
            self.monitoring_groups_table.update_item(
                Key={'group_name': group_name},
                UpdateExpression="SET events = :e",
                ExpressionAttributeValues={':e': new_events},
                ReturnValues="UPDATED_NEW"
            )
            self.logger.info(f"Updated group '{group_name}' successfully")
            return {'success': True, 'message': 'Group updated successfully'}
        except Exception as e:
            self.logger.error(f"Error updating group '{group_name}': {e}")
            return {'success': False, 'error': str(e)}


    def delete_group(self, group_name):
        if group_name:
            try:
                response = self.monitoring_groups_table.delete_item(
                    Key={'group_name': group_name}
                )
                self.logger.info(f"Group '{group_name}' deleted successfully.")
                return {'success': True, 'message': f"Group '{group_name}' deleted successfully.", 'response': response}
            except Exception as e:
                self.logger.error(f"Error deleting group '{group_name}': {str(e)}")
                return {'success': False, 'error': str(e)}
        else:
            error_message = "'group_name' must not be None."
            self.logger.error(error_message)
            return {'success': False, 'error': error_message}

    def get_all_groups(self):
        try:
            response = self.monitoring_groups_table.scan(
                ProjectionExpression="group_name, description"
            )
            groups = [{'group_name': item['group_name'], 'description': item.get('description', '')} for item in
                      response.get('Items', [])]
            self.logger.info(f"Retrieved {len(groups)} groups.")
            return {'success': True, 'data': groups}
        except Exception as e:
            self.logger.error(f"Error retrieving groups: {str(e)}")
            return {'success': False, 'error': str(e)}

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
                    self.logger.info(f"Group '{group_name}' retrieved successfully.")
                    return {'success': True, 'data': group}
                else:
                    self.logger.info(f"No group found for group '{group_name}'.")
                    return {'success': False, 'message': f"No group found for group '{group_name}'."}
            except Exception as e:
                self.logger.error(f"Error retrieving group '{group_name}': {str(e)}")
                return {'success': False, 'error': str(e)}
        else:
            error_message = "'group_name' must not be None."
            self.logger.error(error_message)
            return {'success': False, 'error': error_message}

    def add_user(self, user):
        email = user.get('email')
        if not email:
            error_message = 'Email is required'
            self.logger.error(error_message)
            return {'success': False, 'error': error_message}

        try:
            self.user_table.put_item(Item=user)
            self.logger.info(f"User with email '{email}' added successfully.")
            return {'success': True, 'message': 'User added successfully', 'email': email}
        except Exception as e:
            self.logger.error(f"Error adding user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def delete_user_by_email(self, email):
        try:
            self.user_table.delete_item(Key={'email': email})
            self.logger.info(f"User with email '{email}' deleted successfully.")
            return {'success': True, 'message': f"User with email '{email}' deleted successfully."}
        except Exception as e:
            self.logger.error(f"Error deleting user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_all_users(self):
        try:
            response = self.user_table.scan(
                ProjectionExpression="email"
            )
            users = [{'email': item['email']} for item in response.get('Items', [])]
            self.logger.info(f"Retrieved {len(users)} users.")
            return {'success': True, 'data': users}
        except Exception as e:
            self.logger.error(f"Error retrieving users: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_user_by_email(self, email):
        try:
            response = self.user_table.get_item(Key={'email': email})
            user = response.get('Item', None)
            if user:
                self.logger.info(f"User with email '{email}' retrieved successfully.")
                return {'success': True, 'data': user}
            else:
                self.logger.info(f"No user found with email '{email}'.")
                return {'success': False, 'message': f"No user found with email '{email}'."}
        except NoCredentialsError:
            error_message = "Credentials not available."
            self.logger.error(error_message)
            return {'success': False, 'error': error_message}
        except PartialCredentialsError:
            error_message = "Incomplete credentials provided."
            self.logger.error(error_message)
            return {'success': False, 'error': error_message}
        except Exception as e:
            self.logger.error(f"Error retrieving user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def validate_user(self, email, password):
        user_response = self.get_user_by_email(email)
        if user_response['success']:
            user = user_response['user']
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                self.logger.info(f"User with email '{email}' validated successfully.")
                return {'success': True, 'data': user}
            else:
                self.logger.info(f"Invalid password for user with email '{email}'.")
                return {'success': False, 'message': 'Invalid password'}
        else:
            return user_response

    def change_user_password(self, email, new_hashed_password):
        try:
            self.user_table.update_item(
                Key={'email': email},
                UpdateExpression="SET password = :p",
                ExpressionAttributeValues={':p': new_hashed_password}
            )
            self.logger.info(f"Password for user with email '{email}' updated successfully.")
            return {'success': True, 'message': 'Password updated successfully'}
        except Exception as e:
            self.logger.error(f"Error updating password for user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def save_user_favourite_groups(self, email, favourite_groups):
        try:
            self.user_table.update_item(
                Key={'email': email},
                UpdateExpression="SET favourite_groups = :g",
                ExpressionAttributeValues={':g': favourite_groups}
            )
            self.logger.info(f"Favourite groups for user with email '{email}' updated successfully.")
            return {'success': True, 'message': 'Favourite Groups updated successfully'}
        except Exception as e:
            self.logger.error(f"Error updating favourite groups for user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}


