from pymongo import MongoClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(settings.MONGODB_URI)
            self.db = self.client[settings.MONGODB_NAME]
            logger.info(f"Connected to MongoDB: {settings.MONGODB_NAME}")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise

    def get_collection(self, collection_name):
        if not self.client:
            self.connect()
        return self.db[collection_name]

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

mongodb = MongoDB() 