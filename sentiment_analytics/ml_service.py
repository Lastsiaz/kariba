import os
import pickle
import logging
from typing import Dict, Any, Optional
import numpy as np
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

class SentimentAnalysisService:
    """
    Service class for sentiment analysis using trained SVM model
    """
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'models', 'sentiment_analysis'
        )
        self._load_models()
    
    def _load_models(self):
        """Load the trained models from pickle files"""
        try:
            # Load the SVM classifier
            model_file = os.path.join(self.model_path, 'sentiment_classifier.pkl')
            if os.path.exists(model_file):
                # Check if file is a placeholder
                with open(model_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#'):
                        logger.warning("Model file is a placeholder. Using fallback TextBlob analysis.")
                        self.model = None
                    else:
                        # Try to load as pickle
                        with open(model_file, 'rb') as f:
                            self.model = pickle.load(f)
                        logger.info("SVM model loaded successfully")
            else:
                logger.warning(f"Model file not found: {model_file}")
            
            # Load the vectorizer
            vectorizer_file = os.path.join(self.model_path, 'vectorizer.pkl')
            if os.path.exists(vectorizer_file):
                # Check if file is a placeholder
                with open(vectorizer_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#'):
                        logger.warning("Vectorizer file is a placeholder.")
                        self.vectorizer = None
                    else:
                        # Try to load as pickle
                        with open(vectorizer_file, 'rb') as f:
                            self.vectorizer = pickle.load(f)
                        logger.info("Vectorizer loaded successfully")
            else:
                logger.warning(f"Vectorizer file not found: {vectorizer_file}")
            
            # Load the label encoder
            encoder_file = os.path.join(self.model_path, 'label_encoder.pkl')
            if os.path.exists(encoder_file):
                # Check if file is a placeholder
                with open(encoder_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#'):
                        logger.warning("Label encoder file is a placeholder.")
                        self.label_encoder = None
                    else:
                        # Try to load as pickle
                        with open(encoder_file, 'rb') as f:
                            self.label_encoder = pickle.load(f)
                        logger.info("Label encoder loaded successfully")
            else:
                logger.warning(f"Label encoder file not found: {encoder_file}")
                
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            # Set models to None to use fallback
            self.model = None
            self.vectorizer = None
            self.label_encoder = None
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for sentiment analysis
        
        Args:
            text (str): Input text to preprocess
            
        Returns:
            str: Preprocessed text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and extra whitespace
        import re
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def predict_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Predict sentiment for given text
        
        Args:
            text (str): Input text for sentiment analysis
            
        Returns:
            Dict containing sentiment prediction and confidence
        """
        if not self.model or not self.vectorizer:
            # Fallback to TextBlob analysis
            try:
                from textblob import TextBlob
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                if polarity > 0.1:
                    sentiment = 'positive'
                    confidence = min(abs(polarity), 1.0)
                elif polarity < -0.1:
                    sentiment = 'negative'
                    confidence = min(abs(polarity), 1.0)
                else:
                    sentiment = 'neutral'
                    confidence = 0.5
                
                return {
                    'sentiment': sentiment,
                    'confidence': float(confidence),
                    'method': 'textblob_fallback',
                    'polarity': float(polarity),
                    'processed_text': self.preprocess_text(text)
                }
            except ImportError:
                return {
                    'sentiment': 'neutral',
                    'confidence': 0.5,
                    'error': 'TextBlob not available for fallback analysis',
                    'method': 'fallback_neutral'
                }
        
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            if not processed_text:
                return {
                    'sentiment': 'neutral',
                    'confidence': 0.0,
                    'error': 'Empty text after preprocessing'
                }
            
            # Vectorize the text
            text_vector = self.vectorizer.transform([processed_text])
            
            # Get prediction
            prediction = self.model.predict(text_vector)[0]
            
            # Get prediction probabilities if available
            try:
                probabilities = self.model.predict_proba(text_vector)[0]
                confidence = max(probabilities)
            except:
                # If predict_proba is not available, use decision function
                try:
                    decision_scores = self.model.decision_function(text_vector)
                    confidence = abs(decision_scores[0])
                    # Normalize confidence to 0-1 range
                    confidence = min(confidence, 1.0)
                except:
                    confidence = 0.5
            
            # Decode the prediction if label encoder is available
            if self.label_encoder:
                sentiment = self.label_encoder.inverse_transform([prediction])[0]
            else:
                # Default mapping for common sentiment labels
                sentiment_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}
                sentiment = sentiment_mapping.get(prediction, 'unknown')
            
            return {
                'sentiment': sentiment,
                'confidence': float(confidence),
                'prediction_value': int(prediction),
                'processed_text': processed_text,
                'method': 'ml_model'
            }
            
        except Exception as e:
            logger.error(f"Error predicting sentiment: {str(e)}")
            return {
                'sentiment': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def predict_batch(self, texts: list) -> list:
        """
        Predict sentiment for a batch of texts
        
        Args:
            texts (list): List of input texts
            
        Returns:
            list: List of sentiment predictions
        """
        results = []
        for text in texts:
            result = self.predict_sentiment(text)
            results.append(result)
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            Dict containing model information
        """
        info = {
            'model_loaded': self.model is not None,
            'vectorizer_loaded': self.vectorizer is not None,
            'encoder_loaded': self.label_encoder is not None,
        }
        
        if self.model:
            info.update({
                'model_type': type(self.model).__name__,
                'model_params': self.model.get_params(),
                'n_features': getattr(self.model, 'n_features_in_', 'unknown'),
                'n_classes': len(getattr(self.model, 'classes_', [])) if hasattr(self.model, 'classes_') else 'unknown'
            })
        
        if self.vectorizer:
            info.update({
                'vectorizer_type': type(self.vectorizer).__name__,
                'vocabulary_size': len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 'unknown'
            })
        
        if self.label_encoder:
            info.update({
                'encoder_type': type(self.label_encoder).__name__,
                'classes': self.label_encoder.classes_.tolist() if hasattr(self.label_encoder, 'classes_') else []
            })
        
        return info

# Global instance
sentiment_service = SentimentAnalysisService() 