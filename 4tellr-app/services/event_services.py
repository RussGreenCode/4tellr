import statistics
import pytz
from datetime import datetime, timezone, timedelta
import uuid

from utils.threshold import Threshold
from utils.status_utilities import StatusUtilities
from utils.date_time_utilities import DateTimeUtils

class EventServices:
    def __init__(self, db_helper, logger):
        self.db_helper = db_helper
        self.logger = logger

    def query_events_by_date(self, business_date):
        response = self.db_helper.query_events_by_date(business_date)
        return response['data']

    def query_events_by_date_for_chart(self, business_date):
        query_respone = self.db_helper.query_events_by_date(business_date)

        items=query_respone['data']

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
                        'plotStatus': StatusUtilities.get_plot_status("SLO", outcome_status)
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
                        'plotStatus': StatusUtilities.get_plot_status("SLA", outcome_status)
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
                expected_time = datetime.fromisoformat(time_value).astimezone(utc)
                thresholds = Threshold.get_sla_slo_thresholds(event_name, event_status)

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
            elif event_id.startswith('SLO#') and event_key not in processed_event_keys:
                time_value = item.get('expectedArrival')
                expected_time = datetime.fromisoformat(time_value).astimezone(utc)
                thresholds = Threshold.get_sla_slo_thresholds(event_name, event_status)

                if current_time < (expected_time + thresholds['on_time']):
                    expectation_outcome = 'NOT_REACHED'
                else:
                    expectation_outcome = 'BREACHED'

                if time_value:
                    result.append({
                        'eventId': event_id,
                        'eventType': event_type,
                        'type': 'SLO',
                        'eventKey': event_key,
                        'eventName': event_name,
                        'eventStatus': event_status,
                        'TimeValue': time_value,
                        'outcomeStatus': 'NO_EVT_YET',
                        'plotStatus': expectation_outcome
                    })
            elif event_id.startswith('SLA#') and event_key not in processed_event_keys:
                time_value = item.get('expectedArrival')
                expected_time = datetime.fromisoformat(time_value).astimezone(utc)
                thresholds = Threshold.get_sla_slo_thresholds(event_name, event_status)

                if current_time < (expected_time + thresholds['on_time']):
                    expectation_outcome = 'NOT_REACHED'
                else:
                    expectation_outcome = 'BREACHED'

                if time_value:
                    result.append({
                        'eventId': event_id,
                        'eventType': event_type,
                        'type': 'SLA',
                        'eventKey': event_key,
                        'eventName': event_name,
                        'eventStatus': event_status,
                        'TimeValue': time_value,
                        'outcomeStatus': 'NO_EVT_YET',
                        'plotStatus': expectation_outcome
                    })
            elif event_id.startswith('EVT#') and event_key not in processed_event_keys:
                time_value = item.get('eventTime')
                if event_status == 'ERROR':
                    result.append({
                        'eventId': event_id,
                        'eventType': event_type,
                        'type': 'EVT',
                        'eventKey': event_key,
                        'eventName': event_name,
                        'eventStatus': event_status,
                        'TimeValue': time_value,
                        'outcomeStatus': 'ERROR',
                        'plotStatus': 'ERROR'
                    })
                elif time_value:
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



    def get_monthly_events(self, event_name, event_status):

        # Calculate the start date (one month ago from today)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)


        # Query parameters
        sk_prefix = f'OUT#{event_name}#{event_status}'

        # Perform the query for each day in the date range
        all_events = []
        current_date = start_date
        while current_date <= end_date:
            current_date_str = current_date.strftime('%Y-%m-%d')
            response = self.db_helper.get_event_by_starting_prefix(sk_prefix, current_date_str)
            all_events.extend(response['data'])
            current_date += timedelta(days=1)

        return {
            "events": all_events
        }

    def insert_event(self, event_data):
        event_id = 'EVT#' + event_data['eventName'] + '#' + event_data['eventStatus'] + '#' + str(uuid.uuid4())
        event_data['eventId'] = event_id
        event_data['type'] = 'event'
        event_data['timestamp'] = datetime.now(timezone.utc).isoformat()

        result = self.db_helper.insert_event(event_data)

        if not result['success']:
            return None

        event_time = datetime.fromisoformat(event_data['eventTime'])
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)  # Assuming UTC if not specified
            event_data['eventTime'] = event_time.isoformat()

        if event_data['eventStatus'] == 'ERROR':
            return event_id
        else:
            # Create event outcome
            self.insert_event_outcome(event_data)
            return event_id


    def insert_event_outcome(self, event_data):
        business_date = event_data['businessDate']
        event_name = event_data['eventName']
        event_status = event_data['eventStatus']
        event_time = datetime.fromisoformat(event_data['eventTime'])

        exp_prefix = str(f'EXP#{event_name}#{event_status}')

        # Get expectation for the event using the composite key
        event_result = self.db_helper.get_event_by_starting_prefix(exp_prefix, business_date)


        items = event_result['data']
        slo_time = None
        sla_time = None
        slo_delta = None
        sla_delta = None

        if not items:

            self.logger.info(f'No expectation found for {event_name} with status {event_status} on {business_date}')
            expected_time = None
            str_delta = ''
            outcome_status = 'NEW'

        else:

            # Get Metadata for the event using the composite key - on must be there is an expectaion is there
            metadata_response = self.db_helper.get_event_metadata_by_name_and_status(event_name, event_status)
            event_metadata = metadata_response['data']

            # Assuming there is only one expectation per event_name, event_status, and business_date
            expectation = items[0]
            expected_time = datetime.fromisoformat(expectation['expectedArrival'])
            if expected_time.tzinfo is None:
                expected_time = expected_time.replace(tzinfo=timezone.utc)  # Assuming UTC if not specified

            # how long after the expectation did the event arrive
            delta = event_time - expected_time

            if event_metadata:
                # Get SLA, SLO from metadata
                if event_metadata.get('slo', {}).get('status') == 'active':
                    slo_time_return = DateTimeUtils.t_plus_to_iso(business_date, event_metadata['slo']['time'])
                    slo_time = datetime.fromisoformat(slo_time_return)
                    if slo_time.tzinfo is None:
                        slo_time = slo_time.replace(tzinfo=timezone.utc)
                    slo_delta = slo_time - expected_time

                if event_metadata.get('sla', {}).get('status') == 'active':
                    sla_time_return = DateTimeUtils.t_plus_to_iso(business_date, event_metadata['sla']['time'])
                    sla_time = datetime.fromisoformat(sla_time_return)
                    if sla_time.tzinfo is None:
                        sla_time = sla_time.replace(tzinfo=timezone.utc)
                    sla_delta = sla_time - expected_time

            outcome_status = 'LATE'  # Default outcome status

            if delta <= timedelta(minutes=10):
                outcome_status = 'ON_TIME'
            elif slo_delta is not None and delta <= slo_delta:
                outcome_status = 'MEETS_SLO'
            elif sla_delta is not None and delta <= sla_delta:
                outcome_status = 'MEETS_SLA'

            str_delta = str(delta.total_seconds())

        outcome_data = {
            'type': 'outcome',
            'eventId': 'OUT#' + event_data['eventName'] + '#' + event_data['eventStatus'] + '#' + str(uuid.uuid4()),
            'eventName': event_data['eventName'],
            'eventStatus': event_data['eventStatus'],
            'businessDate': event_data['businessDate'],
            'eventTime': event_time.isoformat(),
            'expectedTime': expected_time.isoformat() if expected_time else None,
            'sloTime': slo_time.isoformat() if slo_time else None,
            'slaTime': sla_time.isoformat() if sla_time else None,
            'delta': str_delta if str_delta else None,
            'outcomeStatus': outcome_status,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        self.db_helper.insert_event(outcome_data)

        self.logger.info(f'Inserted event outcome: {outcome_data["eventId"]}')


    def delete_expectations_for_business_date(self, business_date):

        #Call the db_helper to delete the events.
        response = self.db_helper.delete_expectations_for_business_date(business_date)

        return response['success']

    def delete_events_for_business_dates(self, business_dates):

        response = self.db_helper.delete_events_for_business_dates(business_dates)

        return response['success']

    def generate_expectations(self, business_date):
        response = self.db_helper.get_all_event_metadata()
        metadata_list = response['data']

        self.logger.info(f'Found {len(metadata_list)} metrics for {business_date}')

        for metadata in metadata_list:
            event_name = metadata['event_name']
            event_status = metadata['event_status']


            # Handle expectation
            expectation = metadata.get('expectation', {})
            if expectation['status'] == 'active':
                self.create_expectation_record(business_date, event_name, event_status, expectation, 'expectation','EXP')

            # Handle SLO
            slo = metadata.get('slo', {})
            if slo.get('status') == 'active':
                self.create_expectation_record(business_date, event_name, event_status, slo, 'slo','SLO')

            # Handle SLA
            sla = metadata.get('sla', {})
            if sla.get('status') == 'active':
                self.create_expectation_record(business_date, event_name, event_status, sla, 'sla', 'SLA')

        self.logger.info(f'Created Expectations for {business_date}')
        return True

    def create_expectation_record(self, business_date, event_name, event_status, time_metadata,
                                  record_type, prefix):
        time_delay = time_metadata['time']

        try:
            days = DateTimeUtils.get_days_from_t_format(time_delay)
            hours = DateTimeUtils.get_hours_from_t_format(time_delay)
            minutes = DateTimeUtils.get_minutes_from_t_format(time_delay)
            seconds = DateTimeUtils.get_seconds_from_t_format(time_delay)

            delay_timedelta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        except ValueError as e:
            # Log the error and the problematic string
            print(f"Error parsing delay from '{time_delay}': {e}")
            return  # Skip this iteration and proceed with the next metric

        # Combine the business_date and delay_timedelta to get the expected datetime in UTC
        business_date_dt = datetime.strptime(business_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        expected_datetime = business_date_dt + delay_timedelta

        expectation_id = f'{prefix}#{event_name}#{event_status}#{str(uuid.uuid4())}'
        expectation_data = {
            'type': record_type,
            'eventId': expectation_id,
            'eventName': event_name,
            'eventStatus': event_status,
            'businessDate': business_date,
            'expectedArrival': expected_datetime.isoformat(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        self.db_helper.insert_event(expectation_data)

    def update_expected_times(self, event_names_statuses=None):
        events = self.scan_events_last_month()

        if not events:
            return None

        if event_names_statuses is None:
            event_names_statuses = []

        grouped_events = {}
        for event in events:
            if event['type'] == 'event':
                key = (event['eventName'], event['eventStatus'])
                if not event_names_statuses or key in event_names_statuses:
                    if key not in grouped_events:
                        grouped_events[key] = []
                    grouped_events[key].append(event)

        for (event_name, event_status), group in grouped_events.items():
            try:
                avg_time_elapsed = self.calculate_expected_time(group)
                self.logger.info(f'Storing {event_name}#{event_status} for time after T +: {avg_time_elapsed}')
                if avg_time_elapsed:
                    expectation_time = DateTimeUtils.convert_avg_time_to_t_format(avg_time_elapsed)
                    self.db_helper.update_metadata_with_expectation(event_name, event_status, expectation_time)
            except ValueError as e:
                self.logger.error(f'Failed to update expected times for {event_name}#{event_status}: {e}')

    def scan_events_last_month(self):
        today = datetime.now()
        one_month_ago = today - timedelta(days=30)
        events = []

        for i in range((today - one_month_ago).days + 1):
            day = (one_month_ago + timedelta(days=i)).strftime('%Y-%m-%d')
            events.extend(self.query_events_by_date(day))

        return events

    def calculate_expected_time(self, events):
        utc = pytz.UTC

        debug = False

        times_in_seconds = []
        for event in events:
            event_time = datetime.fromisoformat(event['eventTime']).astimezone(utc)
            business_date_utc = datetime.strptime(event['businessDate'], "%Y-%m-%d").replace(tzinfo=utc)

            # Calculate the total seconds from the start of the business date to the event time
            time_difference = (event_time - business_date_utc).total_seconds()
            times_in_seconds.append(time_difference)


        # Calculate average time excluding outliers
        mean = statistics.mean(times_in_seconds)
        stdev = statistics.stdev(times_in_seconds)


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


    def get_expectation_list(self):
        # Perform a scan to get all items
        response = self.db_helper.get_expectation_list()

        # Return the latest metrics as a list
        return response['data']

    def get_process_stats_list(self):
        # Perform a scan to get all items
        response = self.db_helper.get_process_stats_list()

        # Return the latest metrics as a list
        return response['data']

    def get_process_by_name(self, event_name):
        # Perform a scan to get all items
        response = self.db_helper.get_process_by_name(event_name)

        if not response['success']:
            self.logger.error(f"Error retrieving process for event name: {event_name}")
            return {'success': False, 'error': f"Error retrieving process for event name: {event_name}"}

        process = response['data']

        dependencies = process.get('dependencies', [])

        # Iterate through the dependency list to get the list of processes
        process_list = []

        process_list.append(process)
        for dependency_name in dependencies:
            dependency_response = self.db_helper.get_process_by_name(dependency_name)
            if dependency_response['success']:
                process_list.append(dependency_response['data'])
            else:
                self.logger.error(f"Error retrieving process for dependency: {dependency_name}")

        return process_list

    def create_event_metadata_from_events(self, business_date):

        response = self.db_helper.create_event_metadata_from_events(business_date)

        return response['success']

    def event_metadata_list(self):
        # Perform a scan to get all items
        response = self.db_helper.get_event_metadata_list()

        # Return the latest metrics as a list
        return response['data']

    def get_event_metadata(self, id):
        # Go get teh metadata
        response = self.db_helper.get_event_metadata(id)

        # Return the metadata for the event
        return response['data']

    def update_metadata_with_dependencies(self, event_metadata):

        event_name = event_metadata['event_name']
        event_status = event_metadata['event_status']
        dependencies = event_metadata['dependencies']

        response = self.db_helper.update_metadata_with_dependencies(event_name, event_status, dependencies)

        return response['success']

    def save_event_metadata_dependencies(self, event_metadata):

        response = self.db_helper.save_event_metadata_dependencies(event_metadata)

        return response['success']