from django.db import models
from django.utils import timezone

class SentimentAnalysis(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]

    tweet_id = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES)
    confidence_score = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tweet_id} - {self.sentiment} ({self.confidence_score})"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Sentiment Analyses'

class SentimentKeyword(models.Model):
    keyword = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.keyword

    class Meta:
        ordering = ['keyword']

class SentimentReport(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_tweets = models.IntegerField()
    positive_count = models.IntegerField()
    negative_count = models.IntegerField()
    neutral_count = models.IntegerField()
    average_confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    keywords = models.ManyToManyField(SentimentKeyword)

    def __str__(self):
        return f"{self.title} ({self.start_date.date()} to {self.end_date.date()})"

    class Meta:
        ordering = ['-created_at']
