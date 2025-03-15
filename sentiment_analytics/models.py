from django.db import models
from django.contrib.auth.models import User

class SentimentAnalysis(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral')
    ]

    tweet_id = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    confidence_score = models.FloatField()
    analyzed_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    analyzed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['sentiment', 'analyzed_at']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return f"{self.tweet_id} - {self.sentiment} ({self.confidence_score})"

class AnalysisReport(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_tweets = models.IntegerField()
    positive_count = models.IntegerField()
    negative_count = models.IntegerField()
    neutral_count = models.IntegerField()
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')}" 