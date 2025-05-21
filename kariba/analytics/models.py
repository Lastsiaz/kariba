from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AnalyticsQuery(models.Model):
    QUERY_TYPES = [
        ('sentiment', 'Sentiment Analysis'),
        ('trend', 'Trend Analysis'),
        ('comparison', 'Comparison Analysis'),
        ('demographic', 'Demographic Analysis'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    query_type = models.CharField(max_length=20, choices=QUERY_TYPES)
    parameters = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    last_run = models.DateTimeField(null=True, blank=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_interval = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_query_type_display()})"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Analytics Queries'

class AnalyticsResult(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    query = models.ForeignKey(AnalyticsQuery, related_name='results', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time = models.FloatField(null=True, blank=True)  # in seconds

    def __str__(self):
        return f"Result for {self.query.title} ({self.status})"

    class Meta:
        ordering = ['-created_at']

class DataExport(models.Model):
    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('excel', 'Excel'),
    ]

    title = models.CharField(max_length=200)
    query = models.ForeignKey(AnalyticsQuery, related_name='exports', on_delete=models.CASCADE)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file = models.FileField(upload_to='exports/')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    download_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.format})"

    class Meta:
        ordering = ['-created_at'] 