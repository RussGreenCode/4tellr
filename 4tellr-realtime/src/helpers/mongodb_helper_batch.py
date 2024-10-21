# helpers/mongodb_helper_batch.py

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from datetime import datetime
from bson.objectid import ObjectId
from typing import Dict, List, Any
import logging

class MongoDBHelperBatch:
    def __init__(self, config: Dict[str, str], logger: logging.Logger):
        self.config = config
        self.logger = logger

        try:
            self.client = self._initialize_mongo(config)
            self.db = self.client['4tellr-realtime']
            self.event_collection = self.db['trade_events']
            self.metadata_collection = self.db['event_metadata']
        except Exception as e:
            self.logger.error(f"Error initializing MongoDB collections: {e}")
            raise

    def close(self) -> None:
        if hasattr(self, 'client'):
            self.client.close()
            self.logger.info("MongoDB connection closed.")

    def _initialize_mongo(self, config: Dict[str, str]) -> MongoClient:
        try:
            client = MongoClient(config['MONGO_URI'])
            # Verify connection
            client.admin.command('ping')
            return client
        except ConnectionFailure as e:
            self.logger.error("MongoDB connection failed.")
            raise e

    def _serialize_id(self, doc: Any) -> Any:
        if isinstance(doc, list):
            for item in doc:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
        elif isinstance(doc, dict):
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        return doc

    def bulk_insert_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            result = self.event_collection.insert_many(events)
            return {
                'success': True, 
                'message': f'Inserted {len(result.inserted_ids)} documents successfully'
            }
        except Exception as e:
            self.logger.error(f"Error bulk inserting events: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def query_events_by_date(self, business_date: str) -> Dict[str, Any]:
        try:
            events = list(self.event_collection.find({'businessDate': business_date}))
            return {'success': True, 'data': self._serialize_id(events)}
        except Exception as e:
            self.logger.error(f"Error querying events by date: {e}")
            return {'success': False, 'error': str(e)}

    def get_event_by_name_status_date(self, event_name: str, event_status: str, business_date: str) -> Dict[str, Any]:
        try:
            events = list(self.event_collection.find({
                'businessDate': business_date,
                'eventName': event_name,
                'eventStatus': event_status
            }))
            return {'success': True, 'data': self._serialize_id(events)}
        except Exception as e:
            self.logger.error(f"Error retrieving events: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_event_metadata_by_name_and_status(self, event_name: str, event_status: str) -> Dict[str, Any]:
        try:
            metadata = self.metadata_collection.find_one({
                'event_name': event_name,
                'event_status': event_status
            })
            if metadata:
                return {'success': True, 'data': self._serialize_id(metadata)}
            else:
                return {'success': False, 'error': 'Metadata not found'}
        except Exception as e:
            self.logger.error(f"Error retrieving event metadata: {str(e)}")
            return {'success': False, 'error': str(e)}

    def save_event_metadata_slo_sla(self, event_metadata: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = self.metadata_collection.update_one(
                {
                    'event_name': event_metadata['event_name'], 
                    'event_status': event_metadata['event_status']
                },
                {'$set': event_metadata},
                upsert=True
            )
            if result.modified_count > 0 or result.upserted_id:
                return {'success': True, 'message': 'Event metadata updated successfully'}
            else:
                return {'success': False, 'error': 'No changes made to event metadata'}
        except Exception as e:
            self.logger.error(f"Error saving event metadata: {str(e)}")
            return {'success': False, 'error': str(e)}