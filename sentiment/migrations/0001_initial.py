# Generated by Django 5.1.7 on 2025-03-07 07:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SentimentAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tweet_id', models.CharField(max_length=100, unique=True)),
                ('text', models.TextField()),
                ('sentiment', models.CharField(choices=[('positive', 'Positive'), ('negative', 'Negative'), ('neutral', 'Neutral')], max_length=20)),
                ('confidence_score', models.FloatField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('processed_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Sentiment Analyses',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SentimentKeyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['keyword'],
            },
        ),
        migrations.CreateModel(
            name='SentimentReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('total_tweets', models.IntegerField()),
                ('positive_count', models.IntegerField()),
                ('negative_count', models.IntegerField()),
                ('neutral_count', models.IntegerField()),
                ('average_confidence', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('keywords', models.ManyToManyField(to='sentiment.sentimentkeyword')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
