# services/event_services_batch.py

import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
import logging

class DateTimeUtils:
    @staticmethod
    def t_plus_to_iso(business_date: str, t_plus: str) -> str:
        base_date = datetime.strptime(business_date, '%Y-%m-%d')
        hours = int(t_plus.split('T+')[1])
        target_date = base_date + timedelta(hours=hours)
        return target_date.isoformat()

class EventServicesBatch:
    def __init__(self, db_helper: Any, logger: logging.Logger):
        self.db_helper = db_helper
        self.logger = logger
        self.event_buffer: List[Dict[str, Any]] = []
        self.outcome_buffer: List[Dict[str, Any]] = []
        self.buffer_size = 100

    def insert_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Inserting event: {event_data}")
        transformed_event = self.transform_event(event_data)
        if transformed_event:
            self.event_buffer.append(transformed_event)
            self.logger.info(f"Event added to buffer. Buffer size: {len(self.event_buffer)}")
            
            if transformed_event['eventStatus'] != 'ERROR':
                existing_event_data = self.db_helper.get_event_by_name_status_date(
                    transformed_event['eventName'],
                    transformed_event['eventStatus'],
                    transformed_event['businessDate']
                ).get('data', [])
                outcome = self.insert_event_outcome(transformed_event, existing_event_data)
                if outcome:
                    self.outcome_buffer.append(outcome)
                    self.logger.info(f"Outcome added to buffer. Buffer size: {len(self.outcome_buffer)}")
            
            if len(self.event_buffer) >= self.buffer_size:
                return self.flush_buffer()
        return {'success': True, 'message': 'Event buffered'}

    def flush_buffer(self) -> Dict[str, Any]:
        self.logger.info(f"Flushing buffers. Events: {len(self.event_buffer)}, Outcomes: {len(self.outcome_buffer)}")
        
        event_result = {'success': True, 'message': 'No events to flush', 'events_inserted': 0}
        outcome_result = {'success': True, 'message': 'No outcomes to flush', 'outcomes_inserted': 0}

        if self.event_buffer:
            event_result = self.bulk_insert_events(self.event_buffer)
            self.event_buffer.clear()

        if self.outcome_buffer:
            outcome_result = self.bulk_insert_events(self.outcome_buffer)
            self.outcome_buffer.clear()
        
        if event_result['success'] and outcome_result['success']:
            return {
                'success': True,
                'message': 'Events and outcomes inserted successfully',
                'events_inserted': event_result.get('events_inserted', 0),
                'outcomes_inserted': outcome_result.get('outcomes_inserted', 0)
            }
        else:
            error_message = f"Event insert: {event_result.get('error', 'OK')}, Outcome insert: {outcome_result.get('error', 'OK')}"
            return {
                'success': False,
                'error': error_message,
                'events_inserted': event_result.get('events_inserted', 0),
                'outcomes_inserted': outcome_result.get('outcomes_inserted', 0)
            }

    def bulk_insert_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not events:
            return {'success': True, 'message': 'No events to insert', 'events_inserted': 0}
        
        try:
            result = self.db_helper.bulk_insert_events(events)
            if result['success']:
                return {
                    'success': True,
                    'message': result['message'],
                    'events_inserted': len(events)
                }
            return {
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'events_inserted': 0
            }
        except Exception as e:
            self.logger.error(f"Error in bulk_insert_events: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e), 'events_inserted': 0}

    def transform_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            event_name = event_data['eventName']
            event_status = event_data['eventStatus']
            event_id = f"EVT#{event_name}#{event_status}#{uuid.uuid4()}"
            
            transformed_event = {
                **event_data,
                'eventId': event_id,
                'type': 'event',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            return transformed_event
        except Exception as e:
            self.logger.error(f"Error in transform_event: {str(e)}")
            return None

    def insert_event_outcome(self, event_data: Dict[str, Any], existing_event_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            event_name = event_data['eventName']
            event_status = event_data['eventStatus']
            business_date = event_data['businessDate']
            event_time = datetime.fromisoformat(event_data['eventTime'])
            
            expectations = [e for e in existing_event_data if e['type'] == 'expectation']
            previous_events = [e for e in existing_event_data if e['type'] == 'event']
            
            sequence_number = len(previous_events) + 1
            expectation = next((e for e in expectations if e.get('sequence') == sequence_number), None)
            
            metadata_response = self.db_helper.get_event_metadata_by_name_and_status(event_name, event_status)
            event_metadata = metadata_response.get('data', {})
            
            matching_occurrence = next(
                (o for o in event_metadata.get('daily_occurrences', [])
                 if o.get('sequence') == sequence_number),
                None
            )
            
            slo = matching_occurrence.get('slo') if matching_occurrence else None
            sla = matching_occurrence.get('sla') if matching_occurrence else None
            
            outcome = self.determine_outcome(
                business_date, event_name, event_status, 
                sequence_number, event_time, expectation, slo, sla
            )
            return outcome
        except Exception as e:
            self.logger.error(f"Error in insert_event_outcome: {str(e)}", exc_info=True)
            return None

    def determine_outcome(
        self, business_date: str, event_name: str, event_status: str,
        sequence_number: int, event_time: datetime, expectation: Dict[str, Any],
        slo: Dict[str, Any], sla: Dict[str, Any]
    ) -> Dict[str, Any]:
        slo_time = None
        sla_time = None
        slo_delta = None
        sla_delta = None

        if expectation is None:
            outcome_status = 'NEW'
            delta = None
        else:
            expected_time = datetime.fromisoformat(expectation['expectedArrival'])
            if expected_time.tzinfo is None:
                expected_time = expected_time.replace(tzinfo=timezone.utc)

            delta = event_time - expected_time

            if slo and sla:
                if slo.get('status') == 'active':
                    slo_time = datetime.fromisoformat(
                        DateTimeUtils.t_plus_to_iso(business_date, slo.get('time'))
                    ).replace(tzinfo=timezone.utc)
                    slo_delta = slo_time - expected_time

                if sla.get('status') == 'active':
                    sla_time = datetime.fromisoformat(
                        DateTimeUtils.t_plus_to_iso(business_date, sla.get('time'))
                    ).replace(tzinfo=timezone.utc)
                    sla_delta = sla_time - expected_time

            outcome_status = 'LATE'

            if delta <= timedelta(minutes=10):
                outcome_status = 'ON_TIME'
            elif slo_delta and delta <= slo_delta:
                outcome_status = 'MEETS_SLO'
            elif sla_delta and delta <= sla_delta:
                outcome_status = 'MEETS_SLA'

        return {
            'type': 'outcome',
            'eventId': f"OUT#{event_name}#{event_status}#{uuid.uuid4()}",
            'eventName': event_name,
            'eventStatus': event_status,
            'sequence': sequence_number,
            'businessDate': business_date,
            'eventTime': event_time.isoformat(),
            'expectedTime': expectation['expectedArrival'] if expectation else None,
            'sloTime': slo_time.isoformat() if slo_time else None,
            'slaTime': sla_time.isoformat() if sla_time else None,
            'delta': str(delta.total_seconds()) if delta else None,
            'outcomeStatus': outcome_status,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }