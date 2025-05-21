from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .services import SentimentAnalyzer
from .models import SentimentAnalysis, AnalysisReport
import json
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
    
    context = {
        'recent_analyses': recent_analyses,
        'distribution': distribution
    }
    return render(request, 'sentiment_analytics/dashboard.html', context)

@login_required
def analyze_text(request):
    """Analyze sentiment of submitted text."""
    if request.method == 'POST':
        text = request.POST.get('text', '')
        result = analyzer.analyze_sentiment(text, request.user)
        
        if result:
            return JsonResponse(result)
        return JsonResponse({'error': 'Analysis failed'}, status=400)
    
    return render(request, 'sentiment_analytics/analyze.html')

@login_required
def sentiment_map(request):
    """Display geographical distribution of sentiments."""
    # Get analyses with location data
    analyses = SentimentAnalysis.objects.exclude(location__isnull=True).values('location', 'sentiment')
    
    context = {
        'analyses': json.dumps(list(analyses))
    }
    return render(request, 'sentiment_analytics/map.html', context)

@login_required
def sentiment_trends(request):
    """Display sentiment trends over time."""
    # Get hourly sentiment counts for the last 7 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    
    hourly_counts = SentimentAnalysis.objects.filter(
        analyzed_at__range=(start_date, end_date)
    ).extra({
        'hour': "date_trunc('hour', analyzed_at)"
    }).values('hour', 'sentiment').annotate(count=models.Count('id'))
    
    context = {
        'hourly_counts': json.dumps(list(hourly_counts))
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