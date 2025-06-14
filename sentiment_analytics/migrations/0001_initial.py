# Generated by Django 5.1.6 on 2025-06-09 09:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('total_tweets', models.IntegerField()),
                ('positive_count', models.IntegerField()),
                ('negative_count', models.IntegerField()),
                ('neutral_count', models.IntegerField()),
                ('report_file', models.FileField(blank=True, null=True, upload_to='reports/')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SentimentAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tweet_id', models.CharField(max_length=100, unique=True)),
                ('text', models.TextField()),
                ('sentiment', models.CharField(choices=[('positive', 'Positive'), ('negative', 'Negative'), ('neutral', 'Neutral')], max_length=10)),
                ('confidence_score', models.FloatField()),
                ('analyzed_at', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('analyzed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-analyzed_at'],
                'indexes': [models.Index(fields=['sentiment', 'analyzed_at'], name='sentiment_a_sentime_c6f6d3_idx'), models.Index(fields=['location'], name='sentiment_a_locatio_a6b0de_idx')],
            },
        ),
    ]
