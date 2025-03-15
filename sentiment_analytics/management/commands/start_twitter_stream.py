from django.core.management.base import BaseCommand
from sentiment_analytics.twitter_stream import start_twitter_stream

class Command(BaseCommand):
    help = 'Start the Twitter stream for sentiment analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keywords',
            nargs='+',
            type=str,
            help='Keywords to track in the Twitter stream'
        )

    def handle(self, *args, **options):
        keywords = options.get('keywords')
        self.stdout.write(self.style.SUCCESS('Starting Twitter stream...'))
        
        if keywords:
            self.stdout.write(f'Tracking keywords: {", ".join(keywords)}')
        else:
            self.stdout.write('No keywords specified. Sampling public stream.')
        
        try:
            start_twitter_stream(keywords)
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Twitter stream stopped.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}')) 