# Sentiment Analysis Models

This directory contains machine learning models for sentiment analysis.

## Model Files

The following files should be placed in this directory:

1. `sentiment_classifier.pkl` - The trained sentiment classification model
2. `vectorizer.pkl` - The text vectorizer used for preprocessing
3. `label_encoder.pkl` - The label encoder for sentiment classes

## Training Data

Place your training data CSV files in this directory:

1. `training_data.csv` - Main training dataset
2. `validation_data.csv` - Validation dataset
3. `test_data.csv` - Test dataset

## Model Training

To train the sentiment analysis model:

1. Download the Twitter sentiment analysis dataset from Kaggle
2. Place the dataset in this directory
3. Run the training script:
```bash
python manage.py train_sentiment_model
```

## Model Evaluation

The model's performance metrics will be saved in:
- `evaluation_metrics.json` - Contains accuracy, precision, recall, and F1 scores
- `confusion_matrix.png` - Visual representation of the model's performance

## Model Updates

The models should be retrained periodically with new data to maintain accuracy and relevance. 