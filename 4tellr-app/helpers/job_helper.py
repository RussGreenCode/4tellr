from datetime import datetime, timedelta

from flask import current_app

class JobHelper():
    def __init__(self):
        pass

    @property
    def db_helper(self):
        return current_app.config['DB_HELPER']


    def calculate_job_length_statistics(self, yesterday_str):

        started_events = self.db_helper.query_events_by_date_and_status(yesterday_str, 'STARTED')['data']

        success_events = self.db_helper.query_events_by_date_and_status(yesterday_str, 'SUCCESS')['data']

        job_lengths = []
        for started_event in started_events:
            event_name = started_event['eventName']
            start_time = datetime.fromisoformat(started_event['eventTime'])

            success_event = next((e for e in success_events if e['eventName'] == event_name), None)
            if success_event:
                end_time = datetime.fromisoformat(success_event['eventTime'])
                duration_seconds = (end_time - start_time).total_seconds()
                outcome = success_event['outcomeStatus']
                expected_time = success_event['expectedTime']
                job_lengths.append({
                    'event_name': event_name,
                    'business_date': yesterday_str,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration_seconds': duration_seconds,
                    'expected_tIme': expected_time,
                    'outcome': outcome
                })

        if job_lengths:
            result = self.db_helper.save_job_statistics(job_lengths)

