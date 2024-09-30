from typing import List, Dict, Any
import logging
from helpers.mongodb_helper_batch import MongoDBHelperBatch

class EventServicesBatch:
    def __init__(self, db_helper: MongoDBHelperBatch, logger: logging.Logger):
        self.db_helper = db_helper
        self.logger = logger

    async def insert_events_batch(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        try:
            result = await self.db_helper.bulk_write('trade_events', events)
            self.logger.info(f"Inserted {result['inserted_count']} trade events in a bulk write operation")
            return result
        except Exception as e:
            self.logger.error(f"Failed to insert trade events batch: {e}")
            raise

    def close(self):
        self.db_helper.close()