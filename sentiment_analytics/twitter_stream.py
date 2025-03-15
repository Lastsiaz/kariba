import tweepy
from kafka import KafkaProducer
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class TwitterStreamListener(tweepy.StreamingClient):
    def __init__(self, bearer_token, producer):
        super().__init__(bearer_token)
        self.producer = producer

    def on_data(self, data):
        try:
            tweet_data = json.loads(data)
            self.producer.send(settings.KAFKA_TOPIC, value=tweet_data)
            logger.info(f"Tweet sent to Kafka: {tweet_data.get('id', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Error processing tweet: {str(e)}")
            return True

    def on_error(self, status):
        logger.error(f"Error from Twitter API: {status}")
        if status == 420:  # Rate limit
            return False

class TwitterStreamProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        self.stream = TwitterStreamListener(
            settings.TWITTER_BEARER_TOKEN,
            self.producer
        )

    def start_stream(self, keywords=None):
        try:
            if keywords:
                self.stream.filter(track=keywords)
            else:
                self.stream.sample()
        except Exception as e:
            logger.error(f"Error in stream: {str(e)}")
        finally:
            self.producer.close()

def start_twitter_stream(keywords=None):
    producer = TwitterStreamProducer()
    producer.start_stream(keywords) 