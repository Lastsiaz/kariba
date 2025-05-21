import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from sentiment_analysis_system.mongodb import mongodb
from .models import AnalyticsQuery, AnalyticsResult
import logging
import json
import os
from django.conf import settings
from textblob import TextBlob
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_NAME]
        self.tweets = self.db.tweets

    def execute_query(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Execute an analytics query and store the results."""
        start_time = timezone.now()
        try:
            # Create a new result record
            result = AnalyticsResult.objects.create(
                query=query,
                status='running'
            )
            
            # Execute the appropriate analysis based on query type
            if query.query_type == 'sentiment':
                data = self._analyze_sentiment(query.parameters)
            elif query.query_type == 'trend':
                data = self._analyze_trends(query.parameters)
            elif query.query_type == 'comparison':
                data = self._analyze_comparison(query.parameters)
            elif query.query_type == 'demographic':
                data = self._analyze_demographics(query.parameters)
            else:
                raise ValueError(f"Unsupported query type: {query.query_type}")
            
            # Update result with success
            execution_time = (timezone.now() - start_time).total_seconds()
            result.status = 'completed'
            result.result_data = data
            result.execution_time = execution_time
            result.completed_at = timezone.now()
            result.save()
            
            # Update query last run time
            query.last_run = timezone.now()
            query.save()
            
            return result
        
        except Exception as e:
            # Update result with error
            if result:
                result.status = 'failed'
                result.error_message = str(e)
                result.save()
            raise

    def _analyze_sentiment(self, parameters):
        """Analyze sentiment of tweets based on parameters."""
        pipeline = []
        
        # Match stage for filtering
        match_stage = {"$match": {}}
        
        if 'keywords' in parameters:
            match_stage["$match"]["text"] = {
                "$regex": "|".join(parameters['keywords']),
                "$options": "i"
            }
            
        if 'date_range' in parameters:
            match_stage["$match"]["created_at"] = {
                "$gte": parameters['date_range']['start'],
                "$lte": parameters['date_range']['end']
            }
            
        if match_stage["$match"]:
            pipeline.append(match_stage)
            
        # Group by sentiment
        pipeline.extend([
            {"$group": {
                "_id": "$sentiment_analysis.sentiment",
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$sentiment_analysis.confidence_score"}
            }},
            {"$sort": {"count": -1}}
        ])
        
        results = list(self.tweets.aggregate(pipeline))
        
        return {
            'sentiment_distribution': results,
            'total_tweets': sum(r['count'] for r in results),
            'analysis_parameters': parameters
        }

    def _analyze_trends(self, parameters):
        """Analyze trends over time."""
        pipeline = []
        
        # Match stage for filtering
        match_stage = {"$match": {}}
        
        if 'keywords' in parameters:
            match_stage["$match"]["text"] = {
                "$regex": "|".join(parameters['keywords']),
                "$options": "i"
            }
            
        if 'date_range' in parameters:
            match_stage["$match"]["created_at"] = {
                "$gte": parameters['date_range']['start'],
                "$lte": parameters['date_range']['end']
            }
            
        if match_stage["$match"]:
            pipeline.append(match_stage)
            
        # Group by time interval
        interval = parameters.get('interval', 'day')
        date_format = {
            'hour': '%Y-%m-%d-%H',
            'day': '%Y-%m-%d',
            'week': '%Y-%W',
            'month': '%Y-%m'
        }[interval]
        
        pipeline.extend([
            {"$group": {
                "_id": {
                    "date": {"$dateToString": {"format": date_format, "date": "$created_at"}},
                    "sentiment": "$sentiment_analysis.sentiment"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.date": 1}}
        ])
        
        results = list(self.tweets.aggregate(pipeline))
        
        # Restructure data for time series visualization
        time_series = {}
        for r in results:
            date = r['_id']['date']
            sentiment = r['_id']['sentiment']
            if date not in time_series:
                time_series[date] = {'positive': 0, 'negative': 0, 'neutral': 0}
            time_series[date][sentiment] = r['count']
            
        return {
            'time_series': time_series,
            'interval': interval,
            'analysis_parameters': parameters
        }

    def _analyze_comparison(self, parameters):
        """Compare different aspects of tweets."""
        topics = parameters.get('topics', [])
        if not topics:
            raise ValueError("No topics specified for comparison")
            
        results = {}
        for topic in topics:
            pipeline = [
                {"$match": {
                    "text": {"$regex": topic, "$options": "i"}
                }},
                {"$group": {
                    "_id": "$sentiment_analysis.sentiment",
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$sentiment_analysis.confidence_score"}
                }}
            ]
            
            topic_results = list(self.tweets.aggregate(pipeline))
            results[topic] = {
                'sentiment_distribution': topic_results,
                'total_tweets': sum(r['count'] for r in topic_results)
            }
            
        return {
            'comparison_results': results,
            'topics': topics,
            'analysis_parameters': parameters
        }

    def _analyze_demographics(self, parameters):
        """Analyze demographic information from tweets."""
        pipeline = [
            {"$group": {
                "_id": {
                    "location": "$user.location",
                    "sentiment": "$sentiment_analysis.sentiment"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = list(self.tweets.aggregate(pipeline))
        
        # Restructure data for visualization
        locations = {}
        for r in results:
            location = r['_id']['location'] or 'Unknown'
            sentiment = r['_id']['sentiment']
            if location not in locations:
                locations[location] = {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
            locations[location][sentiment] = r['count']
            locations[location]['total'] += r['count']
            
        return {
            'demographic_distribution': locations,
            'total_locations': len(locations),
            'analysis_parameters': parameters
        }

    def export_results(self, result: AnalyticsResult, format: str) -> str:
        """Export analysis results to various formats."""
        data = result.result_data
        
        # Convert data to DataFrame
        df = pd.DataFrame()
        
        if result.query.query_type == 'sentiment':
            df = pd.DataFrame(data['sentiment_distribution'])
        elif result.query.query_type == 'trend':
            df = pd.DataFrame([(date, data['time_series'][date]) 
                             for date in data['time_series']], 
                             columns=['date', 'sentiment_counts'])
        elif result.query.query_type == 'comparison':
            comparison_data = []
            for topic, results in data['comparison_results'].items():
                for sentiment_data in results['sentiment_distribution']:
                    comparison_data.append({
                        'topic': topic,
                        'sentiment': sentiment_data['_id'],
                        'count': sentiment_data['count'],
                        'confidence': sentiment_data['avg_confidence']
                    })
            df = pd.DataFrame(comparison_data)
        elif result.query.query_type == 'demographic':
            demographic_data = []
            for location, counts in data['demographic_distribution'].items():
                demographic_data.append({
                    'location': location,
                    **counts
                })
            df = pd.DataFrame(demographic_data)
            
        # Create export directory if it doesn't exist
        export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"analysis_{result.query.query_type}_{timestamp}"
        
        # Export based on format
        if format == 'csv':
            filepath = os.path.join(export_dir, f"{filename}.csv")
            df.to_csv(filepath, index=False)
        elif format == 'json':
            filepath = os.path.join(export_dir, f"{filename}.json")
            df.to_json(filepath, orient='records')
        elif format == 'excel':
            filepath = os.path.join(export_dir, f"{filename}.xlsx")
            df.to_excel(filepath, index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
        return filepath 