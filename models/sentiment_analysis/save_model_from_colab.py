"""
Script to save trained SVM model from Google Colab and integrate with Django

This script shows how to:
1. Save your trained model from Google Colab
2. Download the model files to your Django project
3. Test the integration

Usage in Google Colab:
1. Run this script in Colab to save your model
2. Download the saved files to your Django project
3. Test the integration using Django management commands
"""

import pickle
import os
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

def save_model_from_colab(svm_model, vectorizer, label_encoder, output_dir='./'):
    """
    Save the trained model components from Google Colab
    
    Args:
        svm_model: Your trained SVM classifier
        vectorizer: Your text vectorizer (TF-IDF, CountVectorizer, etc.)
        label_encoder: Your label encoder for sentiment classes
        output_dir: Directory to save the files
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the SVM classifier
    model_path = os.path.join(output_dir, 'sentiment_classifier.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(svm_model, f)
    print(f"SVM model saved to: {model_path}")
    
    # Save the vectorizer
    vectorizer_path = os.path.join(output_dir, 'vectorizer.pkl')
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"Vectorizer saved to: {vectorizer_path}")
    
    # Save the label encoder
    encoder_path = os.path.join(output_dir, 'label_encoder.pkl')
    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    print(f"Label encoder saved to: {encoder_path}")
    
    # Create a model info file
    info = {
        'model_type': type(svm_model).__name__,
        'vectorizer_type': type(vectorizer).__name__,
        'encoder_type': type(label_encoder).__name__,
        'n_features': getattr(svm_model, 'n_features_in_', 'unknown'),
        'n_classes': len(getattr(svm_model, 'classes_', [])) if hasattr(svm_model, 'classes_') else 'unknown',
        'classes': label_encoder.classes_.tolist() if hasattr(label_encoder, 'classes_') else []
    }
    
    import json
    info_path = os.path.join(output_dir, 'model_info.json')
    with open(info_path, 'w') as f:
        json.dump(info, f, indent=2)
    print(f"Model info saved to: {info_path}")
    
    return {
        'model_path': model_path,
        'vectorizer_path': vectorizer_path,
        'encoder_path': encoder_path,
        'info_path': info_path
    }

def test_model_loading(model_path, vectorizer_path, encoder_path):
    """
    Test loading the saved model components
    
    Args:
        model_path: Path to the saved SVM model
        vectorizer_path: Path to the saved vectorizer
        encoder_path: Path to the saved label encoder
    """
    
    # Load the model components
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    
    with open(encoder_path, 'rb') as f:
        label_encoder = pickle.load(f)
    
    # Test prediction
    test_texts = [
        "I love this product!",
        "This is terrible, I hate it.",
        "It's okay, nothing special."
    ]
    
    print("Testing model predictions:")
    for text in test_texts:
        # Preprocess and vectorize
        processed_text = text.lower()
        text_vector = vectorizer.transform([processed_text])
        
        # Predict
        prediction = model.predict(text_vector)[0]
        sentiment = label_encoder.inverse_transform([prediction])[0]
        
        print(f"Text: '{text}' -> Sentiment: {sentiment}")
    
    return model, vectorizer, label_encoder

# Example usage in Google Colab:
"""
# After training your model in Colab, run:

# Assuming you have:
# - svm_model: your trained SVM classifier
# - vectorizer: your text vectorizer
# - label_encoder: your label encoder

# Save the model
saved_files = save_model_from_colab(svm_model, vectorizer, label_encoder)

# Test the saved model
model, vectorizer, encoder = test_model_loading(
    saved_files['model_path'],
    saved_files['vectorizer_path'],
    saved_files['encoder_path']
)

# Download the files to your local machine
from google.colab import files
files.download('sentiment_classifier.pkl')
files.download('vectorizer.pkl')
files.download('label_encoder.pkl')
files.download('model_info.json')

# Then copy these files to your Django project's models/sentiment_analysis/ directory
"""

if __name__ == "__main__":
    print("This script is designed to be run in Google Colab")
    print("Please copy the relevant functions to your Colab notebook")
    print("and use them after training your SVM model.") 