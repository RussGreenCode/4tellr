from datetime import datetime, timedelta

from services.event_services import EventServices


class JobServices:
    def __init__(self, db_helper, logger):
        self.db_helper = db_helper
        self.logger = logger
        self.event_helper = EventServices(db_helper, logger)


    def calculate_processes_for_average_outcomes(self):

        outcomes = self.db_helper.get_last_months_average_outcomes()['data']

        self.calculate_processes(None, outcomes, 'monthly_average')

    def calculate_processes_for_business_date(self, business_date):

        if business_date:
            outcomes = self.db_helper.query_outcomes_by_date(business_date)['data']

        self.calculate_processes(business_date, outcomes, 'daily')

    def calculate_processes(self, business_date, outcomes, frequency):
        metadata = self.db_helper.get_all_event_metadata()['data']

        processes = []

        # Group outcomes by event_name and sequence
        grouped_outcomes = {}
        for outcome in outcomes:
            key = (outcome['eventName'], outcome['sequence'])
            if key not in grouped_outcomes:
                grouped_outcomes[key] = []
            grouped_outcomes[key].append(outcome)

        # Process each group of outcomes
        for (event_name, sequence), events in grouped_outcomes.items():
            started_event = next((e for e in events if e['eventStatus'] == 'STARTED'), None)
            success_event = next((e for e in events if e['eventStatus'] == 'SUCCESS'), None)

            if started_event and success_event:
                start_time = datetime.fromisoformat(started_event['eventTime'])
                expected_start_time = datetime.fromisoformat(started_event['expectedTime'])
                end_time = datetime.fromisoformat(success_event['eventTime'])
                expected_end_time = datetime.fromisoformat(success_event['expectedTime'])
                duration_seconds = (end_time - start_time).total_seconds()
                outcome = success_event['outcomeStatus']

                # Retrieve corresponding metadata - only started events have dependencies
                started_event_metadata = next((e for e in metadata if e['event_name'] == event_name and e['event_status'] == 'STARTED'), None)

                processes.append({
                    'event_name': event_name,
                    'sequence': sequence,
                    'business_date': business_date,
                    'frequency': frequency,
                    'start_time': start_time,
                    'expected_start_time': expected_start_time,
                    'end_time': end_time,
                    'expected_end_time': expected_end_time,
                    'duration_seconds': duration_seconds,
                    'outcome': outcome,
                    'dependencies': started_event_metadata.get('dependencies', {}) if started_event_metadata else {}
                })

        # Save job statistics if there are any processes to save
        if processes:
            self.db_helper.save_processes(processes)

    def delete_processes_for_date(self, business_date):

        result = self.db_helper.delete_processes_for_date(business_date)
        return result

    def delete_average_processes(self):

        result = self.db_helper.delete_average_processes()
        return result

    def create_slo_sla_for_metadata_without_them(self, slo_threshold, sla_threshold):
        try:
            # Retrieve all event metadata
            response = self.db_helper.get_all_event_metadata()
            metadata_list = response['data']

            # Initialize a list to hold events without SLO or SLA
            events_without_slo_sla = []

            # Iterate through the metadata
            for metadata in metadata_list:
                # Assume initially that SLO and SLA times are defined
                slo_defined = True
                sla_defined = True

                # Check each daily occurrence for undefined SLO and SLA times
                for occurrence in metadata.get('daily_occurrences', []):
                    if occurrence['slo']['time'] == 'undefined':
                        slo_defined = False
                    if occurrence['sla']['time'] == 'undefined':
                        sla_defined = False

                # If either SLO or SLA is undefined in any occurrence, add to the list
                if not slo_defined or not sla_defined:
                    events_without_slo_sla.append({
                        'event_name': metadata['event_name'],
                        'event_status': metadata['event_status']
                    })

            # Pass the list of events to add SLO and SLA
            self.event_helper.add_slo_sla_to_metadata(events_without_slo_sla, slo_threshold, sla_threshold)
            return {'success': True, 'message': 'SLO and SLA added to metadata successfully'}

        except Exception as e:
            self.logger.error(f"Error in create_slo_sla_for_metadata_without_them: {e}")
            return {'success': False, 'error': str(e)}









