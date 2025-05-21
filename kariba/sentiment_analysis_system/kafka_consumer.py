from kafka import KafkaConsumer
from django.conf import settings
import json
import logging
from .mongodb import mongodb
from textblob import TextBlob

logger = logging.getLogger(__name__)

class TweetConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            settings.KAFKA_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='tweet_analysis_group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.tweets_collection = mongodb.get_collection('tweets')

    def analyze_sentiment(self, text):
        """Analyze sentiment of text using TextBlob."""
        analysis = TextBlob(text)
        # Get polarity score (-1 to 1)
        polarity = analysis.sentiment.polarity
        
        # Determine sentiment category
        if polarity > 0:
            sentiment = 'positive'
        elif polarity < 0:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        return {
            'sentiment': sentiment,
            'polarity': polarity,
            'confidence_score': abs(polarity)
        }

    def process_message(self, message):
        """Process a single message from Kafka."""
        try:
            tweet_data = message.value
            
            # Perform sentiment analysis
            sentiment_result = self.analyze_sentiment(tweet_data['text'])
            tweet_data['sentiment_analysis'] = sentiment_result
            
            # Store in MongoDB
            self.tweets_collection.insert_one(tweet_data)
            logger.info(f"Processed and stored tweet: {tweet_data['id']}")
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    def start_consuming(self):
        """Start consuming messages from Kafka."""
        try:
            logger.info("Starting Kafka consumer...")
            for message in self.consumer:
                self.process_message(message)
        except Exception as e:
            logger.error(f"Error in Kafka consumer: {str(e)}")
        finally:
            self.consumer.close()
            logger.info("Kafka consumer stopped")