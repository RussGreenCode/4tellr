import statistics
import pytz
from datetime import datetime, timezone, timedelta
import uuid

from utils.threshold import Threshold
from utils.status_utilities import StatusUtilities
from utils.date_time_utilities import DateTimeUtils, business_date
from collections import defaultdict

class EventServices:
    def __init__(self, db_helper, logger):
        self.db_helper = db_helper
        self.logger = logger

    def query_events_by_date(self, business_date):
        response = self.db_helper.query_events_by_date(business_date)
        return response['data']

    def get_events_for_chart_by_month(self, year, month):
        start_date = datetime(year, month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1)  # Next month, first day

        summary = defaultdict(lambda: defaultdict(int))

        current_date = start_date
        while current_date < end_date:
            business_date = current_date.strftime('%Y-%m-%d')
            events = self.query_events_by_date_for_chart(business_date)

            for event in events:
                day = current_date.day
                summary[day]['TOTAL_EVENTS'] += 1
                summary[day][event['plotStatus']] += 1

            current_date += timedelta(days=1)

        return summary

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

        event_name = event_data.get('eventName')
        event_status = event_data.get('eventStatus')
        business_date = event_data.get('businessDate')

        event_id = 'EVT#' + event_name + '#' + event_status + '#' + str(uuid.uuid4())
        event_data['eventId'] = event_id
        event_data['type'] = 'event'
        event_data['timestamp'] = datetime.now(timezone.utc).isoformat()

        # Retrieve existing events for the same name, status, and business date
        existing_event_data = self.db_helper.get_event_by_name_status_date(event_name, event_status, business_date).get(
            'data')

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
            self.insert_event_outcome(event_data, existing_event_data)
            return event_id

    def insert_event_outcome(self, event_data, existing_event_data):
        business_date = event_data['businessDate']
        event_name = event_data['eventName']
        event_status = event_data['eventStatus']
        event_time = datetime.fromisoformat(event_data['eventTime'])
        previous_events = []
        expectations = []
        previous_outcomes = []
        expectation = None
        sla = None
        slo = None
        sequence_number = 0



        # Separate events by type: expectations, events, and outcomes
        for existing_event in existing_event_data:
            if existing_event['type'] == 'expectation':
                expectations.append(existing_event)

            elif existing_event['type'] == 'event':
                previous_events.append(existing_event)

            else:
                continue

        # If there are existing expectations, proceed to find the appropriate expectation, SLA, and SLO
        if len(expectations) > 0:
            # Get the metadata for the event, which includes SLAs and SLOs
            metadata_response = self.db_helper.get_event_metadata_by_name_and_status(event_name, event_status)
            event_metadata = metadata_response['data']

            if event_status == 'STARTED':
                # Calculate the current event count for the day, considering only 'STARTED' events
                current_daily_event_count = len(previous_events)

                if current_daily_event_count >= 1:
                    # Check if there are ERROR events
                    error_event_data = self.db_helper.get_event_by_name_status_date(event_name, 'ERROR',
                                                                                    business_date).get('data', [])

                    if len(error_event_data) > 0:
                        # Subtract the count of ERROR events from the current_daily_event_count
                        error_event_count = len(error_event_data)
                        current_daily_event_count -= error_event_count

            elif event_status == 'SUCCESS':
                # Use the count of previous outcomes to determine the sequence
                current_daily_event_count = len(previous_events)
            else:
                return None

            # Retrieve the appropriate daily occurrence from the event_metadata based on the sequence number
            sequence_number = current_daily_event_count + 1
            matching_occurrence = next(
                (occurrence for occurrence in event_metadata.get('daily_occurrences') if
                 occurrence.get('sequence') == sequence_number),
                None
            )

            # Set expectation, SLA, and SLO based on the retrieved values from the matching occurrence
            if matching_occurrence:
                sla = matching_occurrence.get('sla', None)
                slo = matching_occurrence.get('slo', None)

            # Get the correct expectation to match the event occurrence
            expectation = next(
                (expectation for expectation in expectations if expectation.get('sequence') == sequence_number), None)

        else:
            # If no expectations are found, set expectation, SLA, and SLO to None
            expectation = None
            sla = None
            slo = None

        # Determine the outcome based on the business date, event name, event status, event time, and the matched expectation, SLA, and SLO
        self.determine_outcome(business_date, event_name, event_status, sequence_number, event_time, expectation, slo, sla)


    def determine_outcome(self, business_date, event_name, event_status, sequence_number, event_time, expectation, slo, sla):

        slo_time = None
        sla_time = None
        slo_delta = None
        sla_delta = None

        if expectation == None:

            self.logger.info(f'No expectation found for {event_name} with status {event_status} on {business_date}')
            expected_time = None
            str_delta = ''
            outcome_status = 'NEW'

        else:

            expected_time = datetime.fromisoformat(expectation['expectedArrival'])
            if expected_time.tzinfo is None:
                expected_time = expected_time.replace(tzinfo=timezone.utc)  # Assuming UTC if not specified

            # how long after the expectation did the event arrive
            delta = event_time - expected_time

            if slo and sla:
                # Get SLA, SLO from metadata
                if slo.get('status') == 'active':
                    slo_time_return = DateTimeUtils.t_plus_to_iso(business_date, slo.get('time'))
                    slo_time = datetime.fromisoformat(slo_time_return)
                    if slo_time.tzinfo is None:
                        slo_time = slo_time.replace(tzinfo=timezone.utc)
                    slo_delta = slo_time - expected_time

                if sla.get('status') == 'active':
                    sla_time_return = DateTimeUtils.t_plus_to_iso(business_date, sla.get('time'))
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
            'eventId': 'OUT#' + event_name + '#' + event_status + '#' + str(uuid.uuid4()),
            'eventName': event_name,
            'eventStatus': event_status,
            'sequence': sequence_number,
            'businessDate': business_date,
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

            # Check if 'daily_occurrences' exists and is a list
            daily_occurrences = metadata.get('daily_occurrences', [])

            # Iterate through each occurrence in daily_occurrences
            for occurrence in daily_occurrences:
                # Handle expectation
                sequence = occurrence.get('sequence')

                expectation = occurrence.get('expectation', {})
                if expectation.get('status') == 'active':
                    self.create_expectation_record(business_date, event_name, event_status, sequence, expectation, 'expectation',
                                                   'EXP')

                # Handle SLO
                slo = occurrence.get('slo', {})
                if slo.get('status') == 'active':
                    self.create_expectation_record(business_date, event_name, event_status, sequence, slo, 'slo', 'SLO')

                # Handle SLA
                sla = occurrence.get('sla', {})
                if sla.get('status') == 'active':
                    self.create_expectation_record(business_date, event_name, event_status, sequence, sla, 'sla', 'SLA')

        self.logger.info(f'Created Expectations for {business_date}')
        return True

    def create_expectation_record(self, business_date, event_name, event_status, sequence, time_metadata,
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
            'sequence': sequence,
            'businessDate': business_date,
            'expectedArrival': expected_datetime.isoformat(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        self.db_helper.insert_event(expectation_data)

    def update_expected_times(self):
        events = self.scan_events_last_month()

        if not events:
            return None

        # Group events by their event_name and event_status
        grouped_events = {}
        for event in events:
            if event['type'] == 'event' and event['eventStatus'] != 'ERROR':
                key = (event['eventName'], event['eventStatus'])
                if key not in grouped_events:
                    grouped_events[key] = []
                grouped_events[key].append(event)

        # Calculate the expected time for each intraday event
        for (event_name, event_status), group in grouped_events.items():
            try:
                intraday_groups = self.group_events_by_intraday_order(group)
                num_of_days = len(set(event['businessDate'] for event in group))
                num_of_events_per_day = round(sum(len(events) for events in intraday_groups.values()) / num_of_days)
                statistics = []


                for intraday_order in range(1, num_of_events_per_day + 1):
                    if intraday_order in intraday_groups:
                        intraday_events = intraday_groups[intraday_order]
                        avg_time_elapsed = self.calculate_expected_time(intraday_events)
                        standard_deviation = self.calculate_standard_deviation(intraday_events, avg_time_elapsed)
                        monthly_growth = self.calculate_monthly_growth(intraday_events)

                        event_occurrence = {
                            'sequence': intraday_order,
                            'no_events_in_sequence': len(intraday_events),
                            'average_time_elapsed': avg_time_elapsed,
                            'standard_deviation': standard_deviation,
                            'monthly_growth': monthly_growth
                        }

                        statistics.append(event_occurrence)


                if len(statistics) > 0:
                    self.db_helper.update_metadata_with_statistics(event_name, event_status, num_of_events_per_day,
                                                                     statistics)

            except ValueError as e:
                self.logger.error(f'Failed to update expected times for {event_name}#{event_status}: {e}')

        return {'success': True, 'message': "Created Expectations for all events"}

    def calculate_standard_deviation(self, events, avg_time_elapsed):
        times_in_seconds = []
        utc = pytz.UTC

        for event in events:
            event_time = datetime.fromisoformat(event['eventTime']).astimezone(utc)
            business_date_utc = datetime.strptime(event['businessDate'], "%Y-%m-%d").replace(tzinfo=utc)
            time_difference = (event_time - business_date_utc).total_seconds()
            times_in_seconds.append(time_difference)

        # Calculate the standard deviation of the times
        if len(times_in_seconds) > 1:
            stdev = statistics.stdev(times_in_seconds)
        else:
            stdev = 0  # If there's only one event, standard deviation is 0

        return stdev

    def calculate_monthly_growth(self, events):
        # Group events by week
        events_by_week = {}
        utc = pytz.UTC

        for event in events:
            event_time = datetime.fromisoformat(event['eventTime']).astimezone(utc)
            week_start = event_time - timedelta(days=event_time.weekday())
            week_start_str = week_start.strftime('%Y-%m-%d')

            if week_start_str not in events_by_week:
                events_by_week[week_start_str] = []
            events_by_week[week_start_str].append(event)

        # Calculate the number of events per week
        event_counts = [len(events) for week, events in sorted(events_by_week.items())]

        if len(event_counts) > 1:
            # Calculate percentage growth from first week to last week
            initial_count = event_counts[0]
            final_count = event_counts[-1]

            if initial_count > 0:
                growth_percentage = ((final_count - initial_count) / initial_count) * 100
            else:
                growth_percentage = 0  # No growth if the initial count was 0
        else:
            growth_percentage = 0  # No growth if there was only one week

        return growth_percentage

    def group_events_by_intraday_order(self, events):
        intraday_groups = {}
        event_dates = {}

        for event in events:
            date_key = event['businessDate']
            if date_key not in event_dates:
                event_dates[date_key] = []
            event_dates[date_key].append(event)

        for date_key, day_events in event_dates.items():
            day_events.sort(key=lambda x: x['eventTime'])
            for idx, event in enumerate(day_events):
                intraday_order = idx + 1
                if intraday_order not in intraday_groups:
                    intraday_groups[intraday_order] = []
                intraday_groups[intraday_order].append(event)

        return intraday_groups

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

    def get_process_stats_list(self, business_date):

        # Perform a scan to get all items
        response = self.db_helper.get_process_stats_list(business_date)

        # Return the latest metrics as a list
        return response['data']

    def get_process_by_name(self, event_name):
        # Perform a scan to get all items related to the event name
        response = self.db_helper.get_process_by_name(event_name)

        if not response['success']:
            self.logger.error(f"Error retrieving process for event name: {event_name}")
            return []

        processes = response['data']
        process_list = []
        dependency_name_list = []

        # Iterate through the processes to get their dependencies
        for process in processes:
            dependencies = process.get('dependencies', [])

            # Add the main process to the list
            process_list.append(process)

            # Add each dependency's process to the list
            for dependency_name in dependencies:
                if dependency_name not in dependency_name_list:  # Avoid adding duplicate dependencies
                    dependency_response = self.db_helper.get_process_by_name(dependency_name)
                    if dependency_response['success']:
                        dependency_processes = dependency_response['data']
                        # If the dependency itself has multiple processes, add them all
                        if isinstance(dependency_processes, list):
                            process_list.extend(dependency_processes)
                        else:
                            process_list.append(dependency_processes)
                        dependency_name_list.append(dependency_name)
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

    def save_event_metadata(self, event_metadata):

        response = self.db_helper.save_event_metadata(event_metadata)

        return response['success']


    def add_slo_sla_to_metadata(self, events, slo_threshold, sla_threshold):
        if not events:
            return {'success': False, 'message': 'No events provided'}

        if slo_threshold >= sla_threshold:
            return {'success': False, 'message': 'SLA threshold must be greater than SLO threshold'}

        for event in events:
            event_name = event['event_name']
            event_status = event['event_status']

            # Retrieve the event metadata
            event_metadata_response = self.db_helper.get_event_metadata_by_name_and_status(event_name, event_status)
            event_metadata = event_metadata_response.get('data')

            if not event_metadata:
                continue

            # Iterate over each daily occurrence to update SLO and SLA times
            for occurrence in event_metadata.get('daily_occurrences', []):
                # Get the expectation time in T format
                expectation_time_t_format = occurrence['expectation']['time']

                # Calculate the new SLO and SLA times based on the thresholds
                slo_time = DateTimeUtils.add_time_to_t_format(expectation_time_t_format, slo_threshold)
                sla_time = DateTimeUtils.add_time_to_t_format(expectation_time_t_format, sla_threshold)

                # Update the occurrence with new SLO and SLA times
                occurrence['slo'] = {
                    'origin': 'auto',
                    'status': 'active',
                    'time': slo_time,
                    'updated_at': datetime.utcnow().isoformat()
                }

                occurrence['sla'] = {
                    'origin': 'auto',
                    'status': 'active',
                    'time': sla_time,
                    'updated_at': datetime.utcnow().isoformat()
                }

            # Save the updated event metadata back to the database
            self.db_helper.save_event_metadata_slo_sla(event_metadata)

        return {'success': True, 'message': 'SLO and SLA times updated for the provided events'}

    from datetime import datetime

    def create_daily_occurrences_from_statistics(self, params):
        # Get all the event_metadata
        response = self.db_helper.get_all_event_metadata()

        event_metadata_list = response['data']

        for event_metadata in event_metadata_list:
            # Check that the event_metadata has statistics - if not move on to the next one
            if 'statistics' not in event_metadata or not event_metadata['statistics']:
                continue

            # Initialize the daily_occurrences field if not already present
            if 'daily_occurrences' not in event_metadata or not isinstance(event_metadata['daily_occurrences'], list):
                event_metadata['daily_occurrences'] = []

            # Iterate through each entity in the event_metadata.statistics
            for statistic in event_metadata['statistics']:
                sequence = statistic['sequence']

                # Check if there is a corresponding entry in the daily_occurrences
                existing_occurrence = next(
                    (occurrence for occurrence in event_metadata['daily_occurrences'] if
                     occurrence['sequence'] == sequence), None)

                if existing_occurrence:
                    # If there is already one then move on to the next
                    continue

                expected_time = DateTimeUtils.convert_avg_time_to_t_format(statistic['average_time_elapsed'])

                # If there is not one then create an occurrence entity with the initial structure
                occurrence = {
                    "sequence": sequence,
                    "expectation": {
                        "origin": "initial",
                        "status": "active",
                        "time": expected_time,  # Based on the statistics
                        "updated_at": datetime.utcnow().isoformat()
                    },
                    "slo": {
                        "origin": "initial",
                        "status": "inactive",
                        "time": "undefined",
                        "updated_at": datetime.utcnow().isoformat()
                    },
                    "sla": {
                        "origin": "initial",
                        "status": "inactive",
                        "time": "undefined",
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }

                # Append the new occurrence entity to the daily_occurrences list
                event_metadata['daily_occurrences'].append(occurrence)

            # Update the event_metadata document with the new occurrences
            self.db_helper.update_metadata_with_occurrences(event_metadata['event_name'],
                                                            event_metadata['event_status'],
                                                            event_metadata['daily_occurrences'])

        return {'success': True, 'message': "Daily occurrences created or updated from statistics"}
