from flask import jsonify
import bcrypt
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import ConnectionFailure, PyMongoError
from datetime import datetime, timedelta
from helpers.database_helper_interface import DatabaseHelperInterface


class MongoDBHelper(DatabaseHelperInterface):
    def __init__(self, config, logger):
        self.config = config
        self.client = self._initialize_mongo(config)
        self.db = self.client['4tellr']
        self.event_collection = self.db['event_details']
        self.stats_collection = self.db['event_statistics']
        self.groups_collection = self.db['monitoring_groups']
        self.user_collection = self.db['user']
        self.job_stats_collection = self.db['job_statistics']

        # Set up logging
        self.logger = logger

    def _initialize_mongo(self, config):
        try:
            client = MongoClient(config['MONGO_URI'])
            # Verify connection
            client.admin.command('ping')
            return client
        except ConnectionFailure as e:
            self.logger.error("MongoDB connection failed.")
            raise e

    def _serialize_id(self, doc):
        try:
            if isinstance(doc, list):
                for item in doc:
                    if '_id' in item:
                        before = item['_id']
                        item['_id'] = str(item['_id'])
                        after = item['_id']
            #          self.logger.info(f"_serialize_id transformation: before={before}, after={after}")
            elif isinstance(doc, dict):
                if '_id' in doc:
                    before = doc['_id']
                    doc['_id'] = str(doc['_id'])
                    after = doc['_id']
            #      self.logger.info(f"_serialize_id transformation: before={before}, after={after}")
            else:
                self.logger.error(f"Unexpected document structure: {doc}")

        except Exception as e:
            self.logger.error(f"Error in _serialize_id method: {str(e)}")

        return doc

    def insert_event(self, event_data):
        try:
            self.event_collection.insert_one(event_data)
            self.logger.info(f"Inserted event: {event_data['eventId']}")
            return {'success': True, 'message': 'Event inserted successfully'}
        except Exception as e:
            self.logger.error(f"Error storing the event: {e}")
            return {'success': False, 'error': str(e)}

    def query_events_by_date(self, business_date):
        try:
            events = list(self.event_collection.find({'businessDate': business_date}))
            return {'success': True, 'data': self._serialize_id(events)}
        except Exception as e:
            self.logger.error(f"Error querying events by date: {e}")
            return {'success': False, 'error': str(e)}

    def query_events_by_date_and_status(self, business_date, status):
        try:
            events = list(self.event_collection.find({
                'eventStatus': status,
                'businessDate': business_date,
                'type': 'outcome',
            }))
            return {'success': True, 'data': self._serialize_id(events)}
        except Exception as e:
            self.logger.error(f"Error querying events by date: {e}")
            return {'success': False, 'error': str(e)}

    def scan_events_last_month(self):
        try:
            today = datetime.now()
            one_month_ago = today - timedelta(days=30)
            events = list(self.event_collection.find({
                'businessDate': {'$gte': one_month_ago.strftime('%Y-%m-%d'), '$lte': today.strftime('%Y-%m-%d')}
            }))
            return {'success': True, 'data': self._serialize_id(events)}
        except Exception as e:
            self.logger.error(f"Error scanning events for the last month: {e}")
            return {'success': False, 'error': str(e)}

    def query_event_details(self, event_id):
        try:
            event = self.event_collection.find_one({'eventId': event_id})
            if event:
                return {'success': True, 'data': self._serialize_id(event)}
            else:
                return {'success': False, 'message': 'Event not found'}
        except Exception as e:
            self.logger.error(f"Error querying event details: {e}")
            return {'success': False, 'error': str(e)}

    def store_statistic(self, event_name, event_status, avg_time_elapsed):
        try:
            self.stats_collection.update_one(
                {'event_name_and_status': f"{event_name}#{event_status}"},
                {'$set': {
                    'expected_time': avg_time_elapsed,
                    'last_updated': datetime.now().isoformat()
                }},
                upsert=True
            )
            self.logger.info(f"Stored statistic for {event_name}#{event_status}")
            return {'success': True, 'message': 'Statistic stored successfully'}
        except Exception as e:
            self.logger.error(f"Failed to store statistic for {event_name}#{event_status}: {e}")
            return {'success': False, 'error': str(e)}

    def get_expected_time(self, event_name, event_status):
        try:
            stat = self.stats_collection.find_one({'event_name_and_status': f"{event_name}#{event_status}"})
            return {'success': True, 'data': self._serialize_id(stat)}
        except Exception as e:
            self.logger.error(f"Error getting expected time: {e}")
            return {'success': False, 'error': str(e)}

    def get_latest_metrics(self):
        try:
            items = list(self.stats_collection.find())
            latest_metrics = {item['event_name_and_status']: item for item in items}
            return {'success': True, 'data': list(latest_metrics.values())}
        except Exception as e:
            self.logger.error(f"Error getting latest metrics: {e}")
            return {'success': False, 'error': str(e)}

    def delete_expectations_for_business_date(self, business_date):
        try:
            result = self.get_event_by_starting_prefix('EXP#', business_date)
            items = result['data']
            if items is None:
                return {'success': False, 'error': 'Error getting events for deletion'}

            for item in items:
                self.event_collection.delete_one({'_id': item['_id']})
            self.logger.info(f"Deleted {len(items)} expectations for business date {business_date}")
            return {'success': True, 'message': f"Deleted {len(items)} expectations"}
        except Exception as e:
            self.logger.error(f"Error deleting expectations for business date {business_date}: {e}")
            return {'success': False, 'error': str(e)}

    def delete_events_for_business_dates(self, business_dates):
        try:
            for business_date in business_dates:
                items = list(self.event_collection.find({'businessDate': business_date}))
                items_to_delete = [item for item in items if item.get('type') in ['event', 'outcome']]

                for item in items_to_delete:
                    self.event_collection.delete_one({'_id': item['_id']})

                self.logger.info(f"Deleted {len(items_to_delete)} events for business date {business_date}")
            return {'success': True, 'message': 'Events deleted successfully'}
        except Exception as e:
            self.logger.error(f"Error deleting events for business dates: {e}")
            return {'success': False, 'error': str(e)}

    def get_event_by_starting_prefix(self, sk_prefix, current_date_str):
        try:
            events = list(self.event_collection.find({
                'businessDate': current_date_str,
                'eventId': {'$regex': f'^{sk_prefix}'}
            }))
            self.logger.info(f"Retrieved {len(events)} events.")
            return {'success': True, 'data': self._serialize_id(events)}
        except Exception as e:
            self.logger.error(f"Error retrieving events: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_expectation_list(self):
        try:
            items = list(self.stats_collection.find())
            latest_metrics = {item['event_name_and_status']: item for item in items}
            return {'success': True, 'data': self._serialize_id(list(latest_metrics.values()))}
        except Exception as e:
            self.logger.error(f"Error getting expectation list: {e}")
            return {'success': False, 'error': str(e)}

    def save_group(self, group_name, events, description):
        try:
            self.groups_collection.update_one(
                {'group_name': group_name},
                {'$set': {'description': description, 'events': events}},
                upsert=True
            )
            self.logger.info(f"Saved group '{group_name}' successfully")
            return {'success': True, 'message': 'Group saved successfully'}
        except Exception as e:
            self.logger.error(f"Error saving group '{group_name}': {e}")
            return {'success': False, 'error': str(e)}

    def update_group(self, group_name, new_events):
        try:
            self.groups_collection.update_one(
                {'group_name': group_name},
                {'$set': {'events': new_events}},
                return_document=ReturnDocument.AFTER
            )
            self.logger.info(f"Updated group '{group_name}' successfully")
            return {'success': True, 'message': 'Group updated successfully'}
        except Exception as e:
            self.logger.error(f"Error updating group '{group_name}': {e}")
            return {'success': False, 'error': str(e)}

    def delete_group(self, group_name):
        if group_name:
            try:
                result = self.groups_collection.delete_one({'group_name': group_name})
                self.logger.info(f"Group '{group_name}' deleted successfully.")
                return {'success': True, 'message': f"Group '{group_name}' deleted successfully.", 'result': result}
            except Exception as e:
                self.logger.error(f"Error deleting group '{group_name}': {str(e)}")
                return {'success': False, 'error': str(e)}
        else:
            error_message = "'group_name' must not be None."
            self.logger.error(error_message)
            return {'success': False, 'error': error_message}

    def get_all_groups(self):
        try:
            groups = list(self.groups_collection.find({}, {'_id': 0, 'group_name': 1, 'description': 1}))
            self.logger.info(f"Retrieved {len(groups)} groups.")
            return {'success': True, 'data': self._serialize_id(groups)}
        except Exception as e:
            self.logger.error(f"Error retrieving groups: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_group_details(self, group_name):
        if group_name is not None:
            try:
                group = self.groups_collection.find_one({'group_name': group_name})
                if group:
                    self.logger.info(f"Group '{group_name}' retrieved successfully.")
                    return {'success': True, 'data': self._serialize_id(group)}
                else:
                    self.logger.info(f"No group found for group '{group_name}'.")
                    return {'success': False, 'message': f"No group found for group '{group_name}'."}
            except PyMongoError as e:
                self.logger.error(f"Error retrieving group '{group_name}': {str(e)}")
                return {'success': False, 'error': str(e)}
        else:
            error_message = "'group_name' must not be None."
            self.logger.error(error_message)
            return {'success': False, 'error': error_message}

    def delete_user_by_email(self, email):
        try:
            result = self.user_collection.delete_one({'email': email})
            if result.deleted_count > 0:
                self.logger.info(f"User with email '{email}' deleted successfully.")
                return {'success': True, 'message': f"User with email '{email}' deleted successfully."}
            else:
                self.logger.info(f"No user found with email '{email}'.")
                return {'success': False, 'message': f"No user found with email '{email}'."}
        except PyMongoError as e:
            self.logger.error(f"Error deleting user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def add_user(self, user):
        email = user.get('email')
        if not email:
            error_message = 'Email is required'
            self.logger.error(error_message)
            return {'success': False, 'error': error_message}

        try:
            self.user_collection.insert_one(user)
            self.logger.info(f"User with email '{email}' added successfully.")
            return {'success': True, 'message': 'User added successfully', 'email': email}
        except PyMongoError as e:
            self.logger.error(f"Error adding user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_all_users(self):
        try:
            users = list(self.user_collection.find({}, {'email': 1, '_id': 0}))
            self.logger.info(f"Retrieved {len(users)} users.")
            return {'success': True, 'data': self._serialize_id(users)}
        except PyMongoError as e:
            self.logger.error(f"Error retrieving users: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_user_by_email(self, email):
        try:
            user = self.user_collection.find_one({'email': email})
            if user:
                self.logger.info(f"User with email '{email}' retrieved successfully.")
                return {'success': True, 'data': self._serialize_id(user)}
            else:
                self.logger.info(f"No user found with email '{email}'.")
                return {'success': False, 'message': f"No user found with email '{email}'."}
        except PyMongoError as e:
            self.logger.error(f"Error retrieving user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def validate_user(self, email, password):
        user_response = self.get_user_by_email(email)
        if user_response['success']:
            user = user_response['data']
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                self.logger.info(f"User with email '{email}' validated successfully.")
                return {'success': True, 'data': self._serialize_id(user)}
            else:
                self.logger.info(f"Invalid password for user with email '{email}'.")
                return {'success': False, 'message': 'Invalid password'}
        else:
            return user_response

    def change_user_password(self, email, new_hashed_password):
        try:
            result = self.user_collection.update_one(
                {'email': email},
                {'$set': {'password': new_hashed_password}}
            )
            if result.modified_count > 0:
                self.logger.info(f"Password for user with email '{email}' updated successfully.")
                return {'success': True, 'message': 'Password updated successfully'}
            else:
                self.logger.info(f"No user found with email '{email}' to update password.")
                return {'success': False, 'message': f"No user found with email '{email}'."}
        except PyMongoError as e:
            self.logger.error(f"Error updating password for user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def save_user_favourite_groups(self, email, favourite_groups):
        try:
            result = self.user_collection.update_one(
                {'email': email},
                {'$set': {'favourite_groups': favourite_groups}}
            )
            if result.modified_count > 0:
                self.logger.info(f"Favourite groups for user with email '{email}' updated successfully.")
                return {'success': True, 'message': 'Favourite Groups updated successfully'}
            else:
                self.logger.info(f"No user found with email '{email}' to update favourite groups.")
                return {'success': False, 'message': f"No user found with email '{email}'."}
        except PyMongoError as e:
            self.logger.error(f"Error updating favourite groups for user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def save_job_statistics(self, job_lengths):

        try:
            self.job_stats_collection.insert_many(job_lengths)
            self.logger.info(f"Saved '{len(job_lengths)}' stats successfully")
            return {'success': True, 'message': 'Group saved successfully'}
        except Exception as e:
            self.logger.error(f"Error saving stats: {e}")
            return {'success': False, 'error': str(e)}
