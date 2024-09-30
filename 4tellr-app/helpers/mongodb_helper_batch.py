import pymongo
from pymongo.errors import BulkWriteError
from pymongo.operations import InsertOne
from typing import List, Dict, Any
import logging
import time
import asyncio

class MongoDBHelperBatch:
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        try:
            self.client = pymongo.MongoClient(
                self.config['MONGO_URI'],
                maxPoolSize=self.config.get('MAX_POOL_SIZE', 200),
                minPoolSize=self.config.get('MIN_POOL_SIZE', 20),
                socketTimeoutMS=self.config.get('SOCKET_TIMEOUT_MS', 10000),
                connectTimeoutMS=self.config.get('CONNECT_TIMEOUT_MS', 10000),
                retryWrites=True
            )
            self.db = self.client['realtime_events_db']
            self.logger.info("Successfully connected to MongoDB with connection pooling")
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def bulk_write(self, collection: str, documents: List[Dict[str, Any]]) -> Dict[str, int]:
        try:
            start_time = time.time()

            # Prepare bulk write operations
            operations = [InsertOne(doc) for doc in documents]

            # Use an event loop to run the synchronous bulk_write operation asynchronously
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._bulk_write, collection, operations)

            elapsed_time = time.time() - start_time

            self.logger.info(f"Bulk wrote {result.inserted_count} documents into {collection} in {elapsed_time:.2f} seconds")
            return {
                'inserted_count': result.inserted_count
            }

        except BulkWriteError as bwe:
            self.logger.error(f"Bulk write error: {bwe.details}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to bulk write documents into {collection}: {e}")
            raise

    def _bulk_write(self, collection: str, operations: List[InsertOne]) -> pymongo.results.BulkWriteResult:
        return self.db[collection].bulk_write(operations, ordered=False)

    def close(self):
        if self.client:
            self.client.close()
            self.logger.info("Closed MongoDB connection")