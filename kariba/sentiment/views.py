from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import SentimentAnalysis, SentimentKeyword, SentimentReport
from textblob import TextBlob
import json
from django.db import models

@login_required
def sentiment_dashboard(request):
    """Display the sentiment analysis dashboard."""
    recent_analyses = SentimentAnalysis.objects.all().order_by('-created_at')[:10]
    active_keywords = SentimentKeyword.objects.filter(is_active=True)
    recent_reports = SentimentReport.objects.all().order_by('-created_at')[:5]
    
    # Calculate overall sentiment distribution
    total_analyses = SentimentAnalysis.objects.count()
    positive_count = SentimentAnalysis.objects.filter(sentiment='positive').count()
    negative_count = SentimentAnalysis.objects.filter(sentiment='negative').count()
    neutral_count = SentimentAnalysis.objects.filter(sentiment='neutral').count()
    
    context = {
        'recent_analyses': recent_analyses,
        'active_keywords': active_keywords,
        'recent_reports': recent_reports,
        'total_analyses': total_analyses,
        'sentiment_distribution': {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count
        }
    }
    return render(request, 'sentiment/dashboard.html', context)

@login_required
def analyze_text(request):
    """Analyze sentiment of provided text."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
            
            if not text:
                return JsonResponse({'error': 'No text provided'}, status=400)
            
            # Perform sentiment analysis using TextBlob
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            
            # Determine sentiment category
            if polarity > 0:
                sentiment = 'positive'
            elif polarity < 0:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Store analysis result
            analysis_obj = SentimentAnalysis.objects.create(
                tweet_id=f"manual_{timezone.now().timestamp()}",
                text=text,
                sentiment=sentiment,
                confidence_score=abs(polarity)
            )
            
            return JsonResponse({
                'sentiment': sentiment,
                'confidence_score': abs(polarity),
                'analysis_id': analysis_obj.id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'sentiment/analyze.html')

@login_required
def keyword_list(request):
    """Display list of sentiment keywords."""
    keywords = SentimentKeyword.objects.all()
    return render(request, 'sentiment/keyword_list.html', {'keywords': keywords})

@login_required
def add_keyword(request):
    """Add a new sentiment keyword."""
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        if keyword:
            SentimentKeyword.objects.create(keyword=keyword)
            messages.success(request, 'Keyword added successfully!')
        else:
            messages.error(request, 'Please provide a keyword.')
        return redirect('sentiment:keyword_list')
    return render(request, 'sentiment/add_keyword.html')

@login_required
def delete_keyword(request, pk):
    """Delete a sentiment keyword."""
    keyword = get_object_or_404(SentimentKeyword, pk=pk)
    if request.method == 'POST':
        keyword.delete()
        messages.success(request, 'Keyword deleted successfully!')
        return redirect('sentiment:keyword_list')
    return render(request, 'sentiment/delete_keyword.html', {'keyword': keyword})

@login_required
def report_list(request):
    """Display list of sentiment reports."""
    reports = SentimentReport.objects.all()
    return render(request, 'sentiment/report_list.html', {'reports': reports})

@login_required
def create_report(request):
    """Create a new sentiment report."""
    if request.method == 'POST':
        title = request.POST.get('title')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        keywords = request.POST.getlist('keywords')
        
        if all([title, start_date, end_date]):
            # Get analyses within date range
            analyses = SentimentAnalysis.objects.filter(
                created_at__range=[start_date, end_date]
            )
            
            # Calculate statistics
            total_tweets = analyses.count()
            positive_count = analyses.filter(sentiment='positive').count()
            negative_count = analyses.filter(sentiment='negative').count()
            neutral_count = analyses.filter(sentiment='neutral').count()
            average_confidence = analyses.aggregate(avg_confidence=models.Avg('confidence_score'))['avg_confidence'] or 0
            
            # Create report
            report = SentimentReport.objects.create(
                title=title,
                start_date=start_date,
                end_date=end_date,
                total_tweets=total_tweets,
                positive_count=positive_count,
                negative_count=negative_count,
                neutral_count=neutral_count,
                average_confidence=average_confidence
            )
            
            # Add keywords to report
            if keywords:
                report.keywords.add(*SentimentKeyword.objects.filter(id__in=keywords))
            
            messages.success(request, 'Report created successfully!')
            return redirect('sentiment:view_report', pk=report.id)
        else:
            messages.error(request, 'Please fill all required fields.')
    
    keywords = SentimentKeyword.objects.filter(is_active=True)
    return render(request, 'sentiment/create_report.html', {'keywords': keywords})

@login_required
def view_report(request, pk):
    """View a specific sentiment report."""
    report = get_object_or_404(SentimentReport, pk=pk)
    return render(request, 'sentiment/view_report.html', {'report': report})

@login_required
def delete_report(request, pk):
    """Delete a sentiment report."""
    report = get_object_or_404(SentimentReport, pk=pk)
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Report deleted successfully!')
        return redirect('sentiment:report_list')
    return render(request, 'sentiment/delete_report.html', {'report': report})
