import nltk
from textblob import TextBlob
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import logging
from .models import SentimentAnalysis
from sentiment_analysis_system.mongodb import mongodb
from .ml_service import sentiment_service

# Download required NLTK data
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')
except Exception as e:
    logging.error(f"Error downloading NLTK data: {str(e)}")

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self, use_ml_model=True):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.tweets_collection = mongodb.get_collection('tweets')
        self.use_ml_model = use_ml_model
        
        # Check if ML model is available
        self.ml_model_available = sentiment_service.model is not None
        if self.ml_model_available:
            logger.info("ML model is available and will be used for sentiment analysis")
        else:
            logger.warning("ML model not available, falling back to TextBlob")

    def preprocess_text(self, text):
        """Clean and preprocess the text for analysis."""
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            
            # Remove user mentions
            text = re.sub(r'@\w+', '', text)
            
            # Remove hashtags
            text = re.sub(r'#\w+', '', text)
            
            # Remove punctuation
            text = re.sub(r'[^\w\s]', '', text)
            
            # Tokenization
            tokens = word_tokenize(text)
            
            # Remove stopwords and lemmatize
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                     if token not in self.stop_words and len(token) > 2]
            
            return ' '.join(tokens)
        except Exception as e:
            logger.error(f"Error preprocessing text: {str(e)}")
            return text

    def analyze_sentiment_ml(self, text):
        """Analyze sentiment using the trained ML model."""
        try:
            result = sentiment_service.predict_sentiment(text)
            
            if result.get('error'):
                logger.warning(f"ML model error: {result['error']}")
                return None
            
            return {
                'sentiment': result['sentiment'],
                'confidence_score': result['confidence'],
                'method': 'ml_model',
                'prediction_value': result.get('prediction_value'),
                'processed_text': result.get('processed_text', '')
            }
        except Exception as e:
            logger.error(f"Error in ML sentiment analysis: {str(e)}")
            return None

    def analyze_sentiment_textblob(self, text):
        """Analyze sentiment using TextBlob (fallback method)."""
        try:
            # Preprocess the text
            processed_text = self.preprocess_text(text)
            
            # Perform sentiment analysis using TextBlob
            analysis = TextBlob(processed_text)
            
            # Determine sentiment and confidence
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Calculate confidence score (0-1)
            confidence_score = abs(polarity) * (1 - subjectivity)
            
            return {
                'sentiment': sentiment,
                'confidence_score': confidence_score,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'method': 'textblob',
                'processed_text': processed_text
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment with TextBlob: {str(e)}")
            return None

    def analyze_sentiment(self, text, user=None, force_method=None):
        """
        Analyze the sentiment of the given text.
        
        Args:
            text (str): Text to analyze
            user: User performing the analysis
            force_method (str): Force specific method ('ml' or 'textblob')
            
        Returns:
            dict: Sentiment analysis results
        """
        try:
            # Determine which method to use
            if force_method == 'ml' or (self.use_ml_model and self.ml_model_available and force_method != 'textblob'):
                result = self.analyze_sentiment_ml(text)
                if result:
                    return result
                else:
                    logger.warning("ML model failed, falling back to TextBlob")
            
            # Fallback to TextBlob
            return self.analyze_sentiment_textblob(text)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return None

    def analyze_tweet(self, tweet_data, user=None, use_ml=True):
        """Analyze a tweet and store the results."""
        try:
            # Extract relevant information
            tweet_id = tweet_data.get('id_str') or tweet_data.get('id')
            text = tweet_data.get('text', '')
            location = tweet_data.get('user', {}).get('location')
            
            # Perform sentiment analysis
            force_method = 'ml' if use_ml and self.ml_model_available else 'textblob'
            analysis_result = self.analyze_sentiment(text, user, force_method)
            
            if analysis_result:
                # Create sentiment analysis record
                sentiment_analysis = SentimentAnalysis.objects.create(
                    tweet_id=tweet_id,
                    text=text,
                    sentiment=analysis_result['sentiment'],
                    confidence_score=analysis_result['confidence_score'],
                    location=location,
                    analyzed_by=user
                )
                
                # Update tweet document in MongoDB with sentiment analysis
                update_data = {
                    'sentiment_analysis': {
                        'sentiment': analysis_result['sentiment'],
                        'confidence_score': analysis_result['confidence_score'],
                        'method': analysis_result.get('method', 'unknown')
                    }
                }
                
                # Add additional fields based on method
                if analysis_result.get('method') == 'textblob':
                    update_data['sentiment_analysis'].update({
                        'polarity': analysis_result.get('polarity'),
                        'subjectivity': analysis_result.get('subjectivity')
                    })
                elif analysis_result.get('method') == 'ml_model':
                    update_data['sentiment_analysis'].update({
                        'prediction_value': analysis_result.get('prediction_value'),
                        'processed_text': analysis_result.get('processed_text', '')
                    })
                
                self.tweets_collection.update_one(
                    {'id_str': tweet_id},
                    {'$set': update_data}
                )
                
                return sentiment_analysis
            
            return None
        except Exception as e:
            logger.error(f"Error analyzing tweet: {str(e)}")
            return None

    def get_sentiment_distribution(self, start_date=None, end_date=None):
        """Get the distribution of sentiments for a given time period."""
        try:
            query = {}
            if start_date and end_date:
                query['analyzed_at'] = {
                    '$gte': start_date,
                    '$lte': end_date
                }
            
            pipeline = [
                {'$match': query},
                {'$group': {
                    '_id': '$sentiment',
                    'count': {'$sum': 1}
                }}
            ]
            
            results = self.tweets_collection.aggregate(pipeline)
            distribution = {
                'positive': 0,
                'negative': 0,
                'neutral': 0
            }
            
            for result in results:
                distribution[result['_id']] = result['count']
            
            return distribution
        except Exception as e:
            logger.error(f"Error getting sentiment distribution: {str(e)}")
            return None

    def get_model_status(self):
        """Get the status of available sentiment analysis models."""
        return {
            'ml_model_available': self.ml_model_available,
            'textblob_available': True,
            'current_method': 'ml_model' if self.ml_model_available and self.use_ml_model else 'textblob',
            'model_info': sentiment_service.get_model_info() if self.ml_model_available else None
        }

    def compare_methods(self, text):
        """Compare sentiment analysis results from both methods."""
        try:
            ml_result = self.analyze_sentiment_ml(text)
            textblob_result = self.analyze_sentiment_textblob(text)
            
            return {
                'text': text,
                'ml_model': ml_result,
                'textblob': textblob_result,
                'agreement': ml_result and textblob_result and ml_result['sentiment'] == textblob_result['sentiment']
            }
        except Exception as e:
            logger.error(f"Error comparing methods: {str(e)}")
            return None 