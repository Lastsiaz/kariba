from django.core.management.base import BaseCommand
from sentiment_analytics.ml_service import sentiment_service
from sentiment_analytics.services import SentimentAnalyzer
import json

class Command(BaseCommand):
    help = 'Test the ML model integration and sentiment analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--text',
            type=str,
            help='Text to analyze for sentiment',
            default='I love this product!'
        )
        parser.add_argument(
            '--compare',
            action='store_true',
            help='Compare ML model with TextBlob results',
        )
        parser.add_argument(
            '--info',
            action='store_true',
            help='Show model information',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing ML Model Integration'))
        self.stdout.write('=' * 50)
        
        # Show model information
        if options['info']:
            self.show_model_info()
        
        # Test sentiment analysis
        text = options['text']
        self.stdout.write(f'\nAnalyzing text: "{text}"')
        
        # Test ML model directly
        self.stdout.write('\n1. Testing ML Model Directly:')
        ml_result = sentiment_service.predict_sentiment(text)
        self.stdout.write(f'   Result: {json.dumps(ml_result, indent=2)}')
        
        # Test through service
        self.stdout.write('\n2. Testing Through SentimentAnalyzer Service:')
        analyzer = SentimentAnalyzer()
        service_result = analyzer.analyze_sentiment(text)
        self.stdout.write(f'   Result: {json.dumps(service_result, indent=2)}')
        
        # Compare methods if requested
        if options['compare']:
            self.stdout.write('\n3. Comparing Methods:')
            comparison = analyzer.compare_methods(text)
            self.stdout.write(f'   Comparison: {json.dumps(comparison, indent=2)}')
        
        # Show model status
        self.stdout.write('\n4. Model Status:')
        status = analyzer.get_model_status()
        self.stdout.write(f'   Status: {json.dumps(status, indent=2)}')
        
        self.stdout.write(self.style.SUCCESS('\nTest completed successfully!'))

    def show_model_info(self):
        """Display detailed model information"""
        self.stdout.write('\nModel Information:')
        self.stdout.write('-' * 30)
        
        info = sentiment_service.get_model_info()
        
        if info['model_loaded']:
            self.stdout.write(self.style.SUCCESS('✓ SVM Model loaded'))
            self.stdout.write(f'   Type: {info["model_type"]}')
            self.stdout.write(f'   Features: {info["n_features"]}')
            self.stdout.write(f'   Classes: {info["n_classes"]}')
            
            # Show model parameters
            params = info.get('model_params', {})
            self.stdout.write('   Parameters:')
            for key, value in params.items():
                self.stdout.write(f'     {key}: {value}')
        else:
            self.stdout.write(self.style.ERROR('✗ SVM Model not loaded'))
        
        if info['vectorizer_loaded']:
            self.stdout.write(self.style.SUCCESS('✓ Vectorizer loaded'))
            self.stdout.write(f'   Type: {info["vectorizer_type"]}')
            self.stdout.write(f'   Vocabulary size: {info["vocabulary_size"]}')
        else:
            self.stdout.write(self.style.ERROR('✗ Vectorizer not loaded'))
        
        if info['encoder_loaded']:
            self.stdout.write(self.style.SUCCESS('✓ Label Encoder loaded'))
            self.stdout.write(f'   Classes: {info["classes"]}')
        else:
            self.stdout.write(self.style.ERROR('✗ Label Encoder not loaded')) 