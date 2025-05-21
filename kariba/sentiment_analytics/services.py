import nltk
from textblob import TextBlob
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import logging
from .models import SentimentAnalysis
from sentiment_analysis_system.mongodb import mongodb

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
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.tweets_collection = mongodb.get_collection('tweets')

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

    def analyze_sentiment(self, text, user=None):
        """Analyze the sentiment of the given text."""
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
                'subjectivity': subjectivity
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return None

    def analyze_tweet(self, tweet_data, user=None):
        """Analyze a tweet and store the results."""
        try:
            # Extract relevant information
            tweet_id = tweet_data.get('id_str') or tweet_data.get('id')
            text = tweet_data.get('text', '')
            location = tweet_data.get('user', {}).get('location')
            
            # Perform sentiment analysis
            analysis_result = self.analyze_sentiment(text)
            
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
                self.tweets_collection.update_one(
                    {'id_str': tweet_id},
                    {'$set': {
                        'sentiment_analysis': {
                            'sentiment': analysis_result['sentiment'],
                            'confidence_score': analysis_result['confidence_score'],
                            'polarity': analysis_result['polarity'],
                            'subjectivity': analysis_result['subjectivity']
                        }
                    }}
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