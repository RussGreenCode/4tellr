from datetime import datetime, timedelta

from services.event_services import EventServices


class JobServices:
    def __init__(self, db_helper, logger):
        self.db_helper = db_helper
        self.logger = logger
        self.event_helper = EventServices(db_helper, logger)



    def calculate_job_length_statistics(self, business_date):

        started_events = self.db_helper.query_outcomes_by_date_and_status(business_date, 'STARTED')['data']
        success_events = self.db_helper.query_outcomes_by_date_and_status(business_date, 'SUCCESS')['data']
        metadata = self.db_helper.get_all_event_metadata()['data']

        job_lengths = []
        for started_event in started_events:
            event_name = started_event['eventName']
            start_time = datetime.fromisoformat(started_event['eventTime'])
            expected_start_time = datetime.fromisoformat(started_event['expectedTime'])

            success_event = next((e for e in success_events if e['eventName'] == event_name), None)
            event_metadata = next(
                (e for e in metadata if e['event_name'] == event_name and e['event_status'] == 'STARTED'), None)

            if success_event:

                end_time = datetime.fromisoformat(success_event['eventTime'])
                duration_seconds = (end_time - start_time).total_seconds()
                outcome = success_event['outcomeStatus']
                expected_end_time = datetime.fromisoformat(success_event['expectedTime'])
                job_lengths.append({
                    'event_name': event_name,
                    'business_date': business_date,
                    'start_time': start_time,
                    'expected_start_time': expected_start_time,
                    'end_time': end_time,
                    'expected_end_time': expected_end_time,
                    'duration_seconds': duration_seconds,
                    'outcome': outcome,
                    'dependencies': event_metadata.get('dependencies', {})
                })

        if job_lengths:
            result = self.db_helper.save_job_statistics(job_lengths)

    def delete_processes_for_date(self, business_date):

        result = self.db_helper.delete_processes_for_date(business_date)
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
                # Check if both SLO and SLA times are missing
                if (metadata['slo']['time'] == 'undefined') and (metadata['sla']['time'] == 'undefined'):
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








