from django.core.management.base import BaseCommand
from sentiment_analysis_system.kafka_consumer import TweetConsumer

class Command(BaseCommand):
    help = 'Start the Kafka consumer for processing tweets'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Kafka consumer...'))
        consumer = TweetConsumer()
        consumer.start_consuming()