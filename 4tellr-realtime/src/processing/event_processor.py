import json
import logging
from typing import Dict, Any, Tuple
import fastjsonschema
import asyncio
from datetime import datetime, timezone


class EventProcessor:
    def __init__(self, event_services, logger: logging.Logger):
        self.event_services = event_services
        self.logger = logger
        self.validate = self._create_validator()

    def _create_validator(self):
        schema = {
            "type": "object",
            "properties": {
                "process_id": {"type": "string"},
                "trade_id": {"type": "integer"},
                "status": {"type": "string"},
                "timestamp": {"type": "string"},
                "application": {"type": "string"}
            },
            "required": ["trade_id", "status", "timestamp"]
        }
        return fastjsonschema.compile(schema)

    async def validate_message(self, message: Dict[str, Any]) -> bool:
        try:
            await asyncio.to_thread(self.validate, message)
            return True
        except fastjsonschema.JsonSchemaException:
            return False

    def transform_message(self, trade_event: Dict[str, Any]) -> Dict[str, Any]:
        event_name = f"{trade_event.get('process_id', 'unknown')}"
        event_time = datetime.fromisoformat(trade_event.get('timestamp')).replace(tzinfo=timezone.utc)
        
        return {
            'eventName': event_name,
            'tradeId': trade_event.get('trade_id', 'unknown'),
            'eventStatus': trade_event.get('status', 'unknown'),
            'businessDate': event_time.strftime('%Y-%m-%d'),
            'eventTime': event_time.isoformat(),
            'eventType': 'MESSAGE',
            'batchOrRealtime': 'Realtime',
            'resource': 'trading app',
            'message': '',
            'details': {
                'messageId': trade_event.get('trade_id', 'unknown'),
                'messageQueue': 'trade_events',
                'application': trade_event.get('application', 'unknown')
            }
        }

    async def process_message(self, msg: Any) -> Tuple[bool, str]:
        try:
            trade_event = json.loads(msg.value.decode('utf-8'))
            if not await self.validate_message(trade_event):
                error_info = "Invalid message format"
                self.logger.warning(f"{error_info}: {trade_event}")
                return False, error_info

            transformed_event = self.transform_message(trade_event)
            result = self.event_services.insert_event(transformed_event)
            if result['success']:
                self.logger.debug(f"Processed and buffered event: {transformed_event}")
                return True, ""
            else:
                error_info = f"Failed to insert event: {result.get('error', 'Unknown error')}"
                self.logger.error(error_info)
                return False, error_info
        except json.JSONDecodeError as e:
            error_info = f"JSON decode error: {str(e)}"
            self.logger.warning(f"{error_info}. Message: {msg.value}")
            return False, error_info
        except Exception as e:
            error_info = f"Unexpected error: {str(e)}"
            self.logger.error(f"{error_info}. Message: {msg.value}")
            return False, error_info