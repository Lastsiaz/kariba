from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .models import AnalyticsQuery, AnalyticsResult, DataExport
from .services import AnalyticsService
import json
from datetime import datetime, timedelta

analytics_service = AnalyticsService()

@login_required
def analytics_dashboard(request):
    """Display the analytics dashboard."""
    recent_queries = AnalyticsQuery.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    scheduled_queries = AnalyticsQuery.objects.filter(created_by=request.user, is_scheduled=True)
    recent_results = AnalyticsResult.objects.filter(query__created_by=request.user).order_by('-created_at')[:5]
    
    context = {
        'recent_queries': recent_queries,
        'scheduled_queries': scheduled_queries,
        'recent_results': recent_results
    }
    return render(request, 'analytics/dashboard.html', context)

@login_required
def create_query(request):
    """Create a new analytics query."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = AnalyticsQuery.objects.create(
                title=data['title'],
                description=data['description'],
                query_type=data['query_type'],
                parameters=data['parameters'],
                created_by=request.user,
                is_scheduled=data.get('is_scheduled', False),
                schedule_interval=data.get('schedule_interval')
            )
            return JsonResponse({'id': query.id, 'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    # Get query type from URL parameter
    query_type = request.GET.get('type', '')
    return render(request, 'analytics/create_query.html', {'query_type': query_type})

@login_required
def execute_query(request, query_id):
    """Execute an analytics query."""
    query = get_object_or_404(AnalyticsQuery, id=query_id, created_by=request.user)
    
    if request.method == 'POST':
        result = analytics_service.execute_query(query)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': result.status,
                'data': result.result_data,
                'execution_time': result.execution_time
            })
        
        return redirect('analytics:view_result', result_id=result.id)
    
    # GET request - show execution page
    context = {
        'query': query,
        'auto_execute': request.GET.get('auto_execute', 'false').lower() == 'true'
    }
    return render(request, 'analytics/execute_query.html', context)

@login_required
def view_result(request, result_id):
    """Display a specific query result."""
    result = get_object_or_404(AnalyticsResult, id=result_id, query__created_by=request.user)
    
    context = {
        'result': result,
        'query': result.query,
        'chart_data': json.dumps(result.result_data)
    }
    return render(request, 'analytics/view_result.html', context)

@login_required
def query_results(request):
    """Display list of query results with filtering and pagination."""
    results = AnalyticsResult.objects.filter(query__created_by=request.user)
    
    # Apply filters
    filters = {}
    
    query_type = request.GET.get('query_type')
    if query_type:
        results = results.filter(query__query_type=query_type)
        filters['query_type'] = query_type
    
    status = request.GET.get('status')
    if status:
        results = results.filter(status=status)
        filters['status'] = status
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from and date_to:
        results = results.filter(created_at__range=[date_from, date_to])
        filters['date_from'] = date_from
        filters['date_to'] = date_to
    
    sort = request.GET.get('sort', 'created_desc')
    if sort == 'created_asc':
        results = results.order_by('created_at')
    elif sort == 'duration_desc':
        results = results.order_by('-execution_time')
    elif sort == 'duration_asc':
        results = results.order_by('execution_time')
    else:  # created_desc
        results = results.order_by('-created_at')
    filters['sort'] = sort
    
    # Pagination
    paginator = Paginator(results, 10)  # 10 results per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'results': page_obj,
        'filters': filters,
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'analytics/query_results.html', context)

@login_required
def export_result(request, result_id):
    """Export query results in various formats."""
    result = get_object_or_404(AnalyticsResult, id=result_id, query__created_by=request.user)
    format = request.GET.get('format', 'csv')
    
    try:
        filepath = analytics_service.export_results(result, format)
        export = DataExport.objects.create(
            title=f"Export of {result.query.title}",
            format=format,
            query=result.query,
            file=filepath,
            created_by=request.user
        )
        return redirect('analytics:download_export', export_id=export.id)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=400)
        return redirect('analytics:view_result', result_id=result.id)

@login_required
def download_export(request, export_id):
    """Download an exported file."""
    export = get_object_or_404(DataExport, id=export_id, created_by=request.user)
    
    try:
        # Update download count
        export.download_count += 1
        export.save()
        
        # Serve the file
        with open(export.file.path, 'rb') as f:
            response = HttpResponse(f.read())
            response['Content-Type'] = {
                'csv': 'text/csv',
                'json': 'application/json',
                'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }[export.format]
            response['Content-Disposition'] = f'attachment; filename="{export.file.name}"'
            return response
    except FileNotFoundError:
        raise Http404("Export file not found")

@login_required
def schedule_query(request, query_id):
    """Schedule a query for periodic execution."""
    query = get_object_or_404(AnalyticsQuery, id=query_id, created_by=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query.is_scheduled = True
            query.schedule_interval = data['interval']
            query.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def delete_query(request, query_id):
    """Delete an analytics query."""
    query = get_object_or_404(AnalyticsQuery, id=query_id, created_by=request.user)
    
    if request.method == 'POST':
        try:
            query.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def delete_result(request, result_id):
    """Delete a query result."""
    result = get_object_or_404(AnalyticsResult, id=result_id, query__created_by=request.user)
    
    if request.method == 'DELETE':
        try:
            result.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405) 