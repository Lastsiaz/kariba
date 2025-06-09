# SVM Model Integration Guide

This guide explains how to integrate your trained SVM model from Google Colab into the Django sentiment analysis application.

## Overview

The integration provides:
- **ML Service**: Loads and manages the SVM model, vectorizer, and label encoder
- **Enhanced Sentiment Analyzer**: Supports both ML model and TextBlob analysis
- **Testing Interface**: Web-based testing and comparison tools
- **Management Commands**: Command-line testing and debugging tools

## Step 1: Save Your Model from Google Colab

### In Google Colab:

1. **After training your SVM model**, use the provided script to save the model components:

```python
# Copy the functions from save_model_from_colab.py to your Colab notebook
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import pickle
import os

def save_model_from_colab(svm_model, vectorizer, label_encoder, output_dir='./'):
    """Save the trained model components"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save SVM classifier
    with open(os.path.join(output_dir, 'sentiment_classifier.pkl'), 'wb') as f:
        pickle.dump(svm_model, f)
    
    # Save vectorizer
    with open(os.path.join(output_dir, 'vectorizer.pkl'), 'wb') as f:
        pickle.dump(vectorizer, f)
    
    # Save label encoder
    with open(os.path.join(output_dir, 'label_encoder.pkl'), 'wb') as f:
        pickle.dump(label_encoder, f)
    
    print("Model files saved successfully!")

# After training, save your model
save_model_from_colab(your_svm_model, your_vectorizer, your_label_encoder)

# Download the files
from google.colab import files
files.download('sentiment_classifier.pkl')
files.download('vectorizer.pkl')
files.download('label_encoder.pkl')
```

2. **Download the files** to your local machine.

## Step 2: Place Model Files in Django Project

1. **Copy the downloaded files** to your Django project:
   ```
   models/sentiment_analysis/sentiment_classifier.pkl
   models/sentiment_analysis/vectorizer.pkl
   models/sentiment_analysis/label_encoder.pkl
   ```

2. **Verify file structure**:
   ```
   your_project/
   ├── models/
   │   └── sentiment_analysis/
   │       ├── sentiment_classifier.pkl
   │       ├── vectorizer.pkl
   │       ├── label_encoder.pkl
   │       └── README.md
   ├── sentiment_analytics/
   │   ├── ml_service.py
   │   ├── services.py
   │   └── ...
   └── ...
   ```

## Step 3: Test the Integration

### Command Line Testing

1. **Test model loading and basic functionality**:
   ```bash
   python manage.py test_ml_model --info
   ```

2. **Test sentiment analysis**:
   ```bash
   python manage.py test_ml_model --text "I love this product!"
   ```

3. **Compare ML model with TextBlob**:
   ```bash
   python manage.py test_ml_model --text "This is amazing!" --compare
   ```

### Web Interface Testing

1. **Start the Django server**:
   ```bash
   python manage.py runserver
   ```

2. **Navigate to the testing interface**:
   - Go to: `http://localhost:8000/sentiment-analytics/test-ml/`
   - Test with sample texts
   - Compare ML model vs TextBlob results

3. **View model information**:
   - Go to: `http://localhost:8000/sentiment-analytics/model-info/`
   - Check model status and parameters

## Step 4: Integration Features

### Automatic Fallback
- If ML model is not available, the system automatically falls back to TextBlob
- No configuration required - it works out of the box

### Method Selection
You can force specific analysis methods:

```python
from sentiment_analytics.services import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Use ML model only
result = analyzer.analyze_sentiment(text, force_method='ml')

# Use TextBlob only
result = analyzer.analyze_sentiment(text, force_method='textblob')

# Auto-select (prefers ML if available)
result = analyzer.analyze_sentiment(text)
```

### Batch Processing
```python
# Analyze multiple texts
texts = ["I love this!", "I hate this!", "It's okay."]
results = analyzer.predict_batch(texts)
```

### Model Information
```python
# Get model status
status = analyzer.get_model_status()

# Get detailed model info
from sentiment_analytics.ml_service import sentiment_service
info = sentiment_service.get_model_info()
```

## Step 5: API Integration

### REST API Usage
The sentiment analysis is available through the existing API endpoints:

```python
# POST to /sentiment-analytics/analyze/
data = {
    'text': 'Your text here',
    'method': 'ml'  # or 'textblob' or 'auto'
}
```

### Tweet Analysis
The ML model is automatically used for tweet analysis:

```python
# Analyze tweets with ML model
analyzer.analyze_tweet(tweet_data, user=request.user, use_ml=True)
```

## Step 6: Monitoring and Debugging

### Logs
Check Django logs for model loading and prediction information:
```bash
python manage.py runserver --verbosity=2
```

### Model Status
Monitor model availability in the web interface or via API:
```python
status = analyzer.get_model_status()
print(f"ML Model Available: {status['ml_model_available']}")
print(f"Current Method: {status['current_method']}")
```

### Error Handling
The system gracefully handles:
- Missing model files
- Corrupted model files
- Incompatible model versions
- Prediction errors

## Troubleshooting

### Common Issues

1. **Model not loading**:
   - Check file paths and permissions
   - Verify pickle files are not corrupted
   - Check scikit-learn version compatibility

2. **Import errors**:
   - Ensure all required packages are installed
   - Check Python version compatibility

3. **Prediction errors**:
   - Verify vectorizer and model are compatible
   - Check input text preprocessing

### Debug Commands

```bash
# Check model files
ls -la models/sentiment_analysis/

# Test model loading
python manage.py test_ml_model --info

# Test with specific text
python manage.py test_ml_model --text "test text" --compare
```

## Performance Considerations

### Model Loading
- Models are loaded once when the service starts
- Subsequent predictions are fast
- Consider model size and memory usage

### Caching
- Consider implementing caching for frequent predictions
- Use Django's caching framework for repeated analyses

### Scaling
- For high-volume analysis, consider:
  - Model serving with dedicated services
  - Batch processing
  - Asynchronous processing

## Security Considerations

### Model Files
- Keep model files secure and version-controlled
- Consider model file integrity checks
- Implement access controls for model updates

### Input Validation
- Validate and sanitize input text
- Implement rate limiting for API endpoints
- Monitor for adversarial inputs

## Next Steps

1. **Model Updates**: Implement a system for model versioning and updates
2. **Performance Optimization**: Add caching and batch processing
3. **Monitoring**: Implement model performance monitoring
4. **A/B Testing**: Compare ML model vs TextBlob performance
5. **Customization**: Adapt preprocessing for your specific use case

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Django logs
3. Test with the provided management commands
4. Use the web interface for debugging

The integration is designed to be robust and user-friendly, with comprehensive error handling and fallback mechanisms. 