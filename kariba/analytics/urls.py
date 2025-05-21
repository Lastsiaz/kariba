from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('create/', views.create_query, name='create_query'),
    path('results/', views.query_results, name='query_results'),
    path('query/<int:query_id>/execute/', views.execute_query, name='execute_query'),
    path('query/<int:query_id>/schedule/', views.schedule_query, name='schedule_query'),
    path('query/<int:query_id>/delete/', views.delete_query, name='delete_query'),
    path('result/<int:result_id>/', views.view_result, name='view_result'),
    path('result/<int:result_id>/export/', views.export_result, name='export_result'),
    path('result/<int:result_id>/delete/', views.delete_result, name='delete_result'),
    path('export/<int:export_id>/download/', views.download_export, name='download_export'),
] 