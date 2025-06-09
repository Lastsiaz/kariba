from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .services import SentimentAnalyzer
from .models import SentimentAnalysis, AnalysisReport
from .ml_service import sentiment_service
import json
import csv
import os
from django.conf import settings
from django.db import models

analyzer = SentimentAnalyzer()

@login_required
def sentiment_dashboard(request):
    """Display the sentiment analysis dashboard."""
    # Get recent sentiment analysis results
    recent_analyses = SentimentAnalysis.objects.select_related('analyzed_by').order_by('-analyzed_at')[:10]
    
    # Get sentiment distribution for the last 24 hours
    end_date = timezone.now()
    start_date = end_date - timedelta(days=1)
    distribution = analyzer.get_sentiment_distribution(start_date, end_date)
    
    # Get model status
    model_status = analyzer.get_model_status()
    
    context = {
        'recent_analyses': recent_analyses,
        'distribution': distribution,
        'model_status': model_status
    }
    return render(request, 'sentiment_analytics/dashboard.html', context)

@login_required
def analyze_text(request):
    """Analyze sentiment of submitted text."""
    if request.method == 'POST':
        text = request.POST.get('text', '')
        method = request.POST.get('method', 'auto')  # auto, ml, textblob
        
        if method == 'ml':
            result = analyzer.analyze_sentiment(text, request.user, force_method='ml')
        elif method == 'textblob':
            result = analyzer.analyze_sentiment(text, request.user, force_method='textblob')
        else:
            result = analyzer.analyze_sentiment(text, request.user)
        
        if result:
            return JsonResponse(result)
        return JsonResponse({'error': 'Analysis failed'}, status=400)
    
    return render(request, 'sentiment_analytics/analyze.html')

@login_required
def save_training_data(request):
    """Save training data from live streaming to models directory."""
    print("[DEBUG] save_training_data view called")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"[DEBUG] Raw POST data: {data}")
            tweets = data.get('tweets', [])
            print(f"[DEBUG] Number of tweets received: {len(tweets)}")
            if not tweets:
                print("[DEBUG] No tweets provided in request")
                return JsonResponse({'error': 'No tweets provided'}, status=400)
            models_dir = os.path.join(settings.BASE_DIR, 'models', 'sentiment_analysis')
            os.makedirs(models_dir, exist_ok=True)
            training_file = os.path.join(models_dir, 'training_data.csv')
            file_exists = os.path.isfile(training_file)
            with open(training_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(['text', 'sentiment'])
                for tweet in tweets:
                    text = tweet.get('text', '').replace('\n', ' ').strip()
                    sentiment = tweet.get('sentiment', '').lower().strip()
                    if text and sentiment:
                        writer.writerow([text, sentiment])
                        print(f"[DEBUG] Appended tweet: {text[:40]}... | {sentiment}")
            print(f"[DEBUG] Finished writing {len(tweets)} tweets to file: {training_file}")
            return JsonResponse({'success': True, 'count': len(tweets), 'message': f'Successfully saved {len(tweets)} tweets to training data'})
        except Exception as e:
            print(f"[DEBUG] Exception: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        print("[DEBUG] Non-POST request received")
        return JsonResponse({'error': 'Invalid request'}, status=405)

def convert_existing_training_data():
    """Convert existing training_data.csv from old format to new format."""
    try:
        models_dir = os.path.join(settings.BASE_DIR, 'models', 'sentiment_analysis')
        training_file = os.path.join(models_dir, 'training_data.csv')
        backup_file = os.path.join(models_dir, 'training_data_backup.csv')
        
        # Create backup
        if os.path.exists(training_file):
            import shutil
            shutil.copy2(training_file, backup_file)
            print(f"Created backup: {backup_file}")  # Debug log
        
        # Read old format and convert
        converted_data = []
        with open(training_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                text = row.get('tweets_descriptions', '').strip()
                sentiment = row.get('tweets_classification', '').strip().lower()
                
                if text and sentiment:
                    converted_data.append([text, sentiment])
        
        # Write new format
        with open(training_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['text', 'sentiment'])
            writer.writerows(converted_data)
        
        print(f"Converted {len(converted_data)} existing records to new format")  # Debug log
        
    except Exception as e:
        print(f"Error converting existing training data: {str(e)}")  # Debug log

@login_required
def test_ml_model(request):
    """Test the ML model with sample texts."""
    if request.method == 'POST':
        text = request.POST.get('text', '')
        compare = request.POST.get('compare', 'false').lower() == 'true'
        
        if compare:
            result = analyzer.compare_methods(text)
        else:
            result = {
                'text': text,
                'ml_result': analyzer.analyze_sentiment_ml(text),
                'textblob_result': analyzer.analyze_sentiment_textblob(text)
            }
        
        return JsonResponse(result)
    
    # Get model status
    model_status = analyzer.get_model_status()
    
    context = {
        'model_status': model_status,
        'sample_texts': [
            "I love this product! It's amazing!",
            "This is terrible, I hate it.",
            "It's okay, nothing special.",
            "The service was excellent and the staff was very helpful.",
            "I'm disappointed with the quality and customer service."
        ]
    }
    return render(request, 'sentiment_analytics/test_ml.html', context)

@login_required
def model_info(request):
    """Display detailed information about the ML model."""
    model_info = sentiment_service.get_model_info()
    model_status = analyzer.get_model_status()
    
    context = {
        'model_info': model_info,
        'model_status': model_status
    }
    return render(request, 'sentiment_analytics/model_info.html', context)

@login_required
def sentiment_map(request):
    """Display geographical distribution of sentiments."""
    # Get analyses with location data
    analyses = SentimentAnalysis.objects.exclude(location__isnull=True).values('location', 'sentiment')
    
    # Calculate statistics
    total_tweets = SentimentAnalysis.objects.count()
    positive_count = SentimentAnalysis.objects.filter(sentiment='positive').count()
    negative_count = SentimentAnalysis.objects.filter(sentiment='negative').count()
    neutral_count = SentimentAnalysis.objects.filter(sentiment='neutral').count()
    
    # Get location-based statistics
    location_stats = SentimentAnalysis.objects.exclude(location__isnull=True).values('location').annotate(
        total=models.Count('id'),
        positive=models.Count('id', filter=models.Q(sentiment='positive')),
        negative=models.Count('id', filter=models.Q(sentiment='negative')),
        neutral=models.Count('id', filter=models.Q(sentiment='neutral'))
    )
    
    # Generate sample geographic data for demonstration
    # In a real implementation, you would extract coordinates from location data
    sample_geographic_data = [
        {
            'lat': -17.8252, 'lng': 31.0335, 'sentiment': 'positive', 
            'text': 'Great service in Harare!', 'location': 'Harare, Zimbabwe'
        },
        {
            'lat': -17.8252, 'lng': 31.0335, 'sentiment': 'negative', 
            'text': 'Poor experience', 'location': 'Harare, Zimbabwe'
        },
        {
            'lat': -20.1600, 'lng': 28.5850, 'sentiment': 'positive', 
            'text': 'Amazing product!', 'location': 'Bulawayo, Zimbabwe'
        },
        {
            'lat': -20.1600, 'lng': 28.5850, 'sentiment': 'neutral', 
            'text': 'Okay service', 'location': 'Bulawayo, Zimbabwe'
        },
        {
            'lat': -17.8833, 'lng': 31.0333, 'sentiment': 'positive', 
            'text': 'Excellent support', 'location': 'Chitungwiza, Zimbabwe'
        },
        {
            'lat': -17.8833, 'lng': 31.0333, 'sentiment': 'negative', 
            'text': 'Disappointed', 'location': 'Chitungwiza, Zimbabwe'
        },
        {
            'lat': -18.1833, 'lng': 31.5500, 'sentiment': 'positive', 
            'text': 'Love it!', 'location': 'Marondera, Zimbabwe'
        },
        {
            'lat': -18.1833, 'lng': 31.5500, 'sentiment': 'neutral', 
            'text': 'Average', 'location': 'Marondera, Zimbabwe'
        }
    ]
    
    context = {
        'analyses': json.dumps(list(analyses)),
        'location_stats': list(location_stats),
        'geographic_data': json.dumps(sample_geographic_data),
        'total_tweets': total_tweets,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count
    }
    return render(request, 'sentiment_analytics/map.html', context)

@login_required
def sentiment_trends(request):
    """Display sentiment trends over time."""
    # Get hourly sentiment counts for the last 7 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    
    # Get all sentiment analyses in the time range
    analyses = SentimentAnalysis.objects.filter(
        analyzed_at__range=(start_date, end_date)
    ).order_by('analyzed_at')
    
    # Generate hourly data for the last 7 days
    hourly_data = {}
    current_time = start_date.replace(minute=0, second=0, microsecond=0)
    
    while current_time <= end_date:
        hour_key = current_time.strftime('%Y-%m-%d %H:00')
        hourly_data[hour_key] = {
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'total': 0
        }
        current_time += timedelta(hours=1)
    
    # Populate hourly data
    for analysis in analyses:
        hour_key = analysis.analyzed_at.replace(minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:00')
        if hour_key in hourly_data:
            hourly_data[hour_key][analysis.sentiment] += 1
            hourly_data[hour_key]['total'] += 1
    
    # Convert to lists for JavaScript
    labels = []
    positive_data = []
    negative_data = []
    neutral_data = []
    total_data = []
    
    for hour_key, data in sorted(hourly_data.items()):
        labels.append(hour_key)
        positive_data.append(data['positive'])
        negative_data.append(data['negative'])
        neutral_data.append(data['neutral'])
        total_data.append(data['total'])
    
    # Calculate overall statistics
    total_tweets = sum(total_data)
    positive_total = sum(positive_data)
    negative_total = sum(negative_data)
    neutral_total = sum(neutral_data)
    
    positive_percentage = (positive_total / total_tweets * 100) if total_tweets > 0 else 0
    negative_percentage = (negative_total / total_tweets * 100) if total_tweets > 0 else 0
    neutral_percentage = (neutral_total / total_tweets * 100) if total_tweets > 0 else 0
    
    # Generate sample data for demonstration (since we might not have real data yet)
    if total_tweets == 0:
        # Generate sample hourly data
        import random
        for i in range(168):  # 7 days * 24 hours
            labels.append(f"Day {i//24 + 1} Hour {i%24}")
            positive_data.append(random.randint(0, 5))
            negative_data.append(random.randint(0, 3))
            neutral_data.append(random.randint(0, 4))
            total_data.append(positive_data[-1] + negative_data[-1] + neutral_data[-1])
        
        total_tweets = sum(total_data)
        positive_total = sum(positive_data)
        negative_total = sum(negative_data)
        neutral_total = sum(neutral_data)
        
        positive_percentage = (positive_total / total_tweets * 100) if total_tweets > 0 else 0
        negative_percentage = (negative_total / total_tweets * 100) if total_tweets > 0 else 0
        neutral_percentage = (neutral_total / total_tweets * 100) if total_tweets > 0 else 0
    
    context = {
        'labels': json.dumps(labels),
        'positive_data': json.dumps(positive_data),
        'negative_data': json.dumps(negative_data),
        'neutral_data': json.dumps(neutral_data),
        'total_data': json.dumps(total_data),
        'total_tweets': total_tweets,
        'positive_total': positive_total,
        'negative_total': negative_total,
        'neutral_total': neutral_total,
        'positive_percentage': round(positive_percentage, 1),
        'negative_percentage': round(negative_percentage, 1),
        'neutral_percentage': round(neutral_percentage, 1)
    }
    return render(request, 'sentiment_analytics/trends.html', context)

@login_required
def generate_report(request):
    """Generate a sentiment analysis report."""
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        # Get sentiment distribution for the specified period
        distribution = analyzer.get_sentiment_distribution(start_date, end_date)
        
        if distribution:
            report = AnalysisReport.objects.create(
                title=title,
                description=description,
                created_by=request.user,
                start_date=start_date,
                end_date=end_date,
                total_tweets=sum(distribution.values()),
                positive_count=distribution['positive'],
                negative_count=distribution['negative'],
                neutral_count=distribution['neutral']
            )
            return redirect('report_detail', report_id=report.id)
    
    return render(request, 'sentiment_analytics/report_form.html') 