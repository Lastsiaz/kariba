from kafka import KafkaConsumer
from django.conf import settings
import json
import logging
from sentiment_analysis_system.mongodb import mongodb

logger = logging.getLogger(__name__)

class TwitterStreamConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            settings.KAFKA_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='twitter_analysis_group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.tweets_collection = mongodb.get_collection('tweets')

    def process_message(self, message):
        try:
            tweet_data = message.value
            # Store raw tweet in MongoDB
            self.tweets_collection.insert_one(tweet_data)
            logger.info(f"Processed and stored tweet with id: {tweet_data.get('id', 'unknown')}")
            return tweet_data
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None

    def start_consuming(self):
        try:
            for message in self.consumer:
                self.process_message(message)
        except Exception as e:
            logger.error(f"Error in consumer: {str(e)}")
        finally:
            self.consumer.close()

def start_twitter_stream_consumer():
    consumer = TwitterStreamConsumer()
    consumer.start_consuming() 