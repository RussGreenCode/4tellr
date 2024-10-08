import bcrypt
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import ConnectionFailure, PyMongoError
from datetime import datetime, timedelta
from helpers.database_helper_interface import DatabaseHelperInterface
from bson.objectid import ObjectId


class MongoDBHelper(DatabaseHelperInterface):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger


        try:
            self.client = self._initialize_mongo(config)
            self.db = self.client['4tellr']
            self.event_collection = self.db['event_details']
            self.groups_collection = self.db['monitoring_groups']
            self.user_collection = self.db['user']
            self.process_stats_collection = self.db['process_statistics']
            self.event_metadata_collection = self.db['event_metadata']
            self.alerts_collection = self.db['alert_details']
        except Exception as e:
            self.logger.error(f"Error initializing MongoDB collections: {e}")
            raise



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

    def query_outcomes_by_date_and_status(self, business_date, status):
        try:
            events = list(self.event_collection.find({
                'businessDate': business_date,
                'eventStatus': status,
                'type': 'outcome',
            }))
            return {'success': True, 'data': self._serialize_id(events)}
        except Exception as e:
            self.logger.error(f"Error querying events by date: {e}")
            return {'success': False, 'error': str(e)}

    def query_outcomes_by_date(self, business_date):
        try:
            events = list(self.event_collection.find({
                'businessDate': business_date,
                'type': 'outcome',
            }))
            return {'success': True, 'data': self._serialize_id(events)}
        except Exception as e:
            self.logger.error(f"Error querying events by date: {e}")
            return {'success': False, 'error': str(e)}

    from datetime import datetime, timedelta

    def get_last_months_average_outcomes(self):
        try:
            today = datetime.now()
            one_month_ago = today - timedelta(days=30)

            # Query outcomes within the last month
            outcomes = list(self.event_collection.find({
                'type': 'outcome',
                'eventTime': {'$gte': one_month_ago.isoformat(), '$lt': today.isoformat()}
            }))

            # Group outcomes by eventName, eventStatus, and sequence
            grouped_outcomes = {}
            for outcome in outcomes:
                key = (outcome['eventName'], outcome['eventStatus'], outcome.get('sequence'))
                if key not in grouped_outcomes:
                    grouped_outcomes[key] = []
                grouped_outcomes[key].append(outcome)

            # Calculate average outcomes for each group
            averaged_outcomes = []
            for (event_name, event_status, sequence), events in grouped_outcomes.items():

                # Initialize total deltas
                total_event_time_delta = 0
                total_expected_time_delta = 0
                total_slo_time_delta = 0
                total_sla_time_delta = 0
                count = len(events)

                for e in events:

                    # Convert businessDate to a datetime object
                    business_date = datetime.fromisoformat(e['businessDate'])
                    # Ensure business_date is offset-aware if event times are offset-aware
                    if datetime.fromisoformat(e['eventTime']).tzinfo:
                        business_date = business_date.replace(tzinfo=datetime.fromisoformat(e['eventTime']).tzinfo)

                    event_time_delta = datetime.fromisoformat(e['eventTime']) - business_date
                    expected_time_delta = datetime.fromisoformat(e['expectedTime']) - business_date
                    slo_time_delta = (
                                datetime.fromisoformat(e['sloTime']) - business_date) if 'sloTime' in e else timedelta(
                        0)
                    sla_time_delta = (
                                datetime.fromisoformat(e['slaTime']) - business_date) if 'slaTime' in e else timedelta(
                        0)

                    total_event_time_delta += event_time_delta.total_seconds()
                    total_expected_time_delta += expected_time_delta.total_seconds()
                    total_slo_time_delta += slo_time_delta.total_seconds()
                    total_sla_time_delta += sla_time_delta.total_seconds()

                # Average the deltas
                avg_event_time_delta = total_event_time_delta / count
                avg_expected_time_delta = total_expected_time_delta / count
                avg_slo_time_delta = total_slo_time_delta / count
                avg_sla_time_delta = total_sla_time_delta / count

                today_date = datetime.fromisoformat(datetime.today().date().isoformat())

                # Add the average deltas back to the business date
                avg_event_time = today_date + timedelta(seconds=avg_event_time_delta)
                avg_expected_time = today_date + timedelta(seconds=avg_expected_time_delta)
                avg_slo_time = today_date + timedelta(
                    seconds=avg_slo_time_delta) if total_slo_time_delta > 0 else None
                avg_sla_time = today_date + timedelta(
                    seconds=avg_sla_time_delta) if total_sla_time_delta > 0 else None

                # Assuming outcome status is the most common one in the group (ON_TIME, DELAYED, etc.)
                outcome_statuses = [e['outcomeStatus'] for e in events]
                avg_outcome_status = max(set(outcome_statuses), key=outcome_statuses.count)

                averaged_outcomes.append({
                    'eventName': event_name,
                    'eventStatus': event_status,
                    'sequence': sequence,
                    'businessDate': today_date.date().isoformat(),  # Use today's date as a placeholder
                    'eventTime': avg_event_time.isoformat(),
                    'expectedTime': avg_expected_time.isoformat(),
                    'sloTime': avg_slo_time.isoformat() if avg_slo_time else None,
                    'slaTime': avg_sla_time.isoformat() if avg_sla_time else None,
                    'delta': avg_event_time_delta,
                    'outcomeStatus': avg_outcome_status
                })

            return {'success': True, 'data': self._serialize_id(averaged_outcomes)}
        except Exception as e:
            self.logger.error(f"Error calculating last month's average outcomes: {e}")
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

    def delete_expectations_for_business_date(self, business_date):
        try:
            result = self.get_events_by_type_and_date(business_date)
            items = result['data']
            if items is None:
                return {'success': False, 'error': 'Error getting events for deletion'}

            for item in items:
                if isinstance(item['_id'], str):
                    item['_id'] = ObjectId(item['_id'])
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

    def get_event_by_name_status_date(self, event_name, event_status, business_date):
        try:
            events = list(self.event_collection.find({
                'businessDate': business_date,
                'eventName': event_name,
                'eventStatus': event_status
            }))
            self.logger.info(f"Retrieved {len(events)} events.")
            return {'success': True, 'data': self._serialize_id(events)}
        except Exception as e:
            self.logger.error(f"Error retrieving events: {str(e)}")
            return {'success': False, 'error': str(e)}


    def get_events_by_type_and_date(self, business_date):
        try:
            events = list(self.event_collection.find({
                'businessDate': business_date,
                'type': {'$in': ['expectation', 'slo', 'sla']}
            }))
            self.logger.info(f"Retrieved {len(events)} events.")
            return {'success': True, 'data': self._serialize_id(events)}
        except Exception as e:
            self.logger.error(f"Error retrieving events: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_expectation_list(self):
        try:
            # Fetch all documents from event_metadata_collection
            items = list(self.event_metadata_collection.find())

            # Create a list of dictionaries with unique event_name#event_status combinations
            unique_event_name_status = [{'event_name_and_status': f"{item['event_name']}#{item['event_status']}"} for
                                        item in items]

            # Convert the set to a list and return
            return {'success': True, 'data': unique_event_name_status}
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
            groups = list(self.groups_collection.find({}, {'_id': 0, 'group_name': 1, 'description': 1, 'events': 1}))
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

        # Add favourite_groups and favourite_alerts as empty arrays
        user['favourite_groups'] = []
        user['favourite_alerts'] = []

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

    def save_user_favourite_alerts(self, email, favourite_alerts):
        try:
            result = self.user_collection.update_one(
                {'email': email},
                {'$set': {'favourite_alerts': favourite_alerts}}
            )
            if result.modified_count > 0:
                self.logger.info(f"Favourite alerts for user with email '{email}' updated successfully.")
                return {'success': True, 'message': 'Favourite alerts updated successfully'}
            else:
                self.logger.info(f"No user found with email '{email}' to update favourite alerts.")
                return {'success': False, 'message': f"No user found with email '{email}'."}
        except PyMongoError as e:
            self.logger.error(f"Error updating favourite alerts for user with email '{email}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def save_processes(self, processes):

        try:
            self.process_stats_collection.insert_many(processes)
            self.logger.info(f"Saved '{len(processes)}' stats successfully")
            return {'success': True, 'message': 'Group saved successfully'}
        except Exception as e:
            self.logger.error(f"Error saving stats: {e}")
            return {'success': False, 'error': str(e)}

    def get_process_stats_list(self, business_date):
        try:
            # Query the database with a filter on business_date
            items = list(self.process_stats_collection.find(
                {'business_date': business_date}
            ))

            # Convert ObjectId to string and datetime to ISO format
            for item in items:
                item['_id'] = str(item['_id'])
                for time_field in ['start_time', 'end_time', 'expected_start_time', 'expected_end_time']:
                    if item.get(time_field):
                        item[time_field] = item[time_field].isoformat()

            return {'success': True, 'data': items}
        except Exception as e:
            self.logger.error(f"Error getting process stats: {e}")
            return {'success': False, 'error': str(e)}

    def get_process_by_name(self, event_name):
        try:
            process_statistics = list(self.process_stats_collection.find({'event_name': event_name, 'frequency': 'monthly_average'}))
            if process_statistics:
                self.logger.info(f"Processes with name '{event_name}' retrieved successfully.")
                return {'success': True, 'data': self._serialize_id(process_statistics)}
            else:
                self.logger.info(f"No process found with name '{event_name}'.")
                return {'success': False, 'message': f"No process found with name '{event_name}'."}
        except PyMongoError as e:
            self.logger.error(f"Error retrieving process with name '{event_name}': {str(e)}")
            return {'success': False, 'error': str(e)}

    def delete_processes_for_date(self, business_date):
        try:
            # Perform the deletion
            result = self.process_stats_collection.delete_many({'business_date': business_date})

            self.logger.info(
                f"Deleted {result.deleted_count} processes for business date {business_date.strftime('%Y-%m-%d')}")
            return {'success': True, 'message': f"Deleted {result.deleted_count} processes"}
        except Exception as e:
            self.logger.error(f"Error deleting processes for business date {business_date}: {e}")
            return {'success': False, 'error': str(e)}


    def delete_average_processes(self):
        try:
            # Perform the deletion
            result = self.process_stats_collection.delete_many({'frequency': 'monthly_average'})

            self.logger.info(
                f"Deleted {result.deleted_count} average processes")
            return {'success': True, 'message': f"Deleted {result.deleted_count} average processes"}
        except Exception as e:
            self.logger.error(f"Error deleting average processes: {e}")
            return {'success': False, 'error': str(e)}

    def create_event_metadata_from_events(self, business_date):
        try:
            statuses = ('SUCCESS', 'STARTED')
            # Find unique eventName/eventStatus combinations
            pipeline = [
                {'$match': {'businessDate': business_date, 'eventStatus': {'$in': statuses}}},
                {'$group': {'_id': {'eventName': '$eventName', 'eventStatus': '$eventStatus'}}}
            ]
            unique_combinations = list(self.event_collection.aggregate(pipeline))

            # Insert into event_metadata if not exists
            for combination in unique_combinations:
                event_name = combination['_id']['eventName']
                event_status = combination['_id']['eventStatus']
                current_time = datetime.now().isoformat()

                if not self.event_metadata_collection.find_one(
                        {'event_name': event_name, 'event_status': event_status}):
                    self.event_metadata_collection.insert_one({
                        'event_name': event_name,
                        'event_status': event_status,
                        'business_date': business_date,
                        'expectation': {'origin': 'initial',
                                        'status': 'inactive',
                                        'time': 'undefined',
                                        'updated_at': current_time},
                        'slo': {'origin': 'initial',
                                'status': 'inactive',
                                'time': 'undefined',
                                'updated_at': current_time},
                        'sla': {'origin': 'initial',
                                'status': 'inactive',
                                'time': 'undefined',
                                'updated_at': current_time},
                    })
                    print(f'Inserted: {event_name}, {event_status}')
                else:
                    print(f'Already exists: {event_name}, {event_status}')
            return {'success': True, 'message': 'Metadata events saved successfully'}
        except Exception as e:
            self.logger.error(f"Error saving Metadata events: {e}")
            return {'success': False, 'error': str(e)}

    def get_event_metadata_list(self):
        try:
            items = list(self.event_metadata_collection.find({}, {
                'event_name': 1,
                'event_status': 1
            }))

            return {'success': True, 'data': self._serialize_id(items)}
        except Exception as e:
            self.logger.error(f"Error getting latest process stats: {e}")
            return {'success': False, 'error': str(e)}

    def get_event_metadata(self, event_id):
        try:
            object_id = ObjectId(event_id)
            metadata = self.event_metadata_collection.find_one({'_id': object_id})
            if metadata:
                return {'success': True, 'data': self._serialize_id(metadata)}
            else:
                return {'success': False, 'message': 'No metadata found for the provided ID'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


    def get_event_info_by_date(self, event_name, event_status, business_date):
        try:
            event_data = list(self.event_collection.find({'businessDate': business_date,
                                                        'eventName': event_name,
                                                        'eventStatus': event_status,
                                                        'type': 'outcome'}))
            if event_data:
                return {'success': True, 'data': self._serialize_id(event_data)}
            else:
                return {'success': False, 'message': 'No event data found for the provided ID'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_event_metadata_by_name_and_status(self, event_name, event_status):
        try:

            metadata = self.event_metadata_collection.find_one({'event_name': event_name, 'event_status': event_status})
            if metadata:
                return {'success': True, 'data': self._serialize_id(metadata)}
            else:
                return {'success': False, 'message': 'No metadata found for event'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def save_event_metadata(self, event_metadata):

        event_name = event_metadata.get('event_name')
        event_status = event_metadata.get('event_status')
        expectation_time = event_metadata.get('expectation_time')
        slo_time = event_metadata.get('slo_time')
        sla_time = event_metadata.get('sla_time')
        current_time = datetime.now().isoformat()


        try:
            result = self.event_metadata_collection.update_one(
                {'event_name': event_name, 'event_status': event_status},
                {'$set': {'expectation': {'origin': 'manual',
                                          'status': 'active',
                                          'time': expectation_time,
                                          'updated_at': current_time},
                          'slo': {'origin': 'manual',
                                  'status': 'active',
                                  'time': slo_time,
                                  'updated_at': current_time},
                          'sla': {'origin': 'manual',
                                  'status': 'active',
                                  'time': sla_time,
                                  'updated_at': current_time}}
                 }
            )
            self.logger.info(f"Event with name: '{event_name}' added successfully.")
            return {'success': True, 'message': 'Event Metadata saved successfully'}
        except Exception as e:
            self.logger.error(f"Error saving Metadata: {e}")
            return {'success': False, 'error': str(e)}

    def save_event_metadata_slo_sla(self, event_metadata):

        event_name = event_metadata.get('event_name')
        event_status = event_metadata.get('event_status')


        try:
            result = self.event_metadata_collection.update_one(
                {'event_name': event_name, 'event_status': event_status},
                {'$set': {'daily_occurrences': event_metadata.get('daily_occurrences')}
                 }
            )
            self.logger.info(f"Metadata with name: '{event_name}' added successfully.")
            return {'success': True, 'message': 'Event Metadata saved successfully'}
        except Exception as e:
            self.logger.error(f"Error saving Metadata: {e}")
            return {'success': False, 'error': str(e)}


    def update_metadata_with_statistics(self, event_name, event_status, num_of_events_per_day, statistics):
        try:
            result = self.event_metadata_collection.update_one(
                {'event_name': event_name, 'event_status': event_status},
                {'$set': {
                    'statistics': statistics,
                    'num_of_events_per_day': num_of_events_per_day
                }}
            )

            if result.matched_count == 0:
                self.logger.warning(
                    f"No record found for event_name: '{event_name}' and event_status: '{event_status}'. No update was performed.")
                return {'success': False,
                        'message': f"No record found for event_name: '{event_name}' and event_status: '{event_status}'"}

            self.logger.info(
                f"Event statistics with name: '{event_name}' and status: '{event_status}' updated successfully.")
            return {'success': True, 'message': 'Event Metadata saved successfully'}

        except Exception as e:
            self.logger.error(f"Error saving Metadata: {e}")
            return {'success': False, 'error': str(e)}

    def update_metadata_with_occurrences(self, event_name, event_status, occurrences):
        try:
            result = self.event_metadata_collection.update_one(
                {'event_name': event_name, 'event_status': event_status},
                {'$set': {
                    'daily_occurrences': occurrences
                }}
            )

            if result.matched_count == 0:
                self.logger.warning(
                    f"No record found for event_name: '{event_name}' and event_status: '{event_status}'. No update was performed.")
                return {'success': False,
                        'message': f"No record found for event_name: '{event_name}' and event_status: '{event_status}'"}

            self.logger.info(
                f"Event occurrences with name: '{event_name}' and status: '{event_status}' updated successfully.")
            return {'success': True, 'message': 'Event Metadata saved successfully'}

        except Exception as e:
            self.logger.error(f"Error saving Metadata: {e}")
            return {'success': False, 'error': str(e)}

    def update_metadata_with_dependencies(self, event_name, event_status, dependencies):
        try:
            result = self.event_metadata_collection.update_one(
                {'event_name': event_name, 'event_status': event_status},
                {'$set': {'dependencies': dependencies}}
            )
            self.logger.info(f"Event with name: '{event_name}' and status: '{event_status}' updated successfully.")
            return {'success': True, 'message': 'Event Metadata saved successfully'}
        except Exception as e:
            self.logger.error(f"Error saving Metadata: {e}")
            return {'success': False, 'error': str(e)}

    def get_all_event_metadata(self):
        try:
            metadata_cursor = self.event_metadata_collection.find({})
            metadata_list = list(metadata_cursor)

            if metadata_list:
                return {'success': True, 'data': self._serialize_id(metadata_list)}
            else:
                return {'success': False, 'message': 'No metadata found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def save_alert(self, alert_name, description, group_name):
        try:
            self.alerts_collection.insert_one(
                {'alert_name': alert_name, 'description': description, 'group_name': group_name}
            )
            self.logger.info(f"Saved alert '{alert_name}' successfully")
            return {'success': True, 'message': 'Alert saved successfully'}
        except Exception as e:
            self.logger.error(f"Error saving alert '{alert_name}': {e}")
            return {'success': False, 'error': str(e)}


    def update_alert(self, alert_name, description, group_name):
        try:
            self.alerts_collection.update_one({'alert_name': alert_name},
                {'$set':{'description': description, 'group_name': group_name}}
            )
            self.logger.info(f"Updated alert '{alert_name}' successfully")
            return {'success': True, 'message': 'Alert updated successfully'}
        except Exception as e:
            self.logger.error(f"Error updating alert '{alert_name}': {e}")
            return {'success': False, 'error': str(e)}

    def get_all_alerts(self):
        try:
            alert_cursor = self.alerts_collection.find({})
            alerts = list(alert_cursor)

            if alerts:
                return {'success': True, 'data': self._serialize_id(alerts)}
            else:
                return {'success': False, 'message': 'No alerts found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_alert(self, alert_name):
        if alert_name:
            try:
                result = self.alerts_collection.delete_one({'alert_name': alert_name})
                self.logger.info(f"Alert '{alert_name}' deleted successfully.")
                return {'success': True, 'message': f"Alert '{alert_name}' deleted successfully.", 'result': result}
            except Exception as e:
                self.logger.error(f"Error deleting alert '{alert_name}': {str(e)}")
                return {'success': False, 'error': str(e)}
        else:
            error_message = "'alert_name' must not be None."
            self.logger.error(error_message)
            return {'success': False, 'error': error_message}