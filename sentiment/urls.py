from django.urls import path
from . import views

app_name = 'sentiment'

urlpatterns = [
    path('', views.sentiment_dashboard, name='dashboard'),
    path('analyze/', views.analyze_text, name='analyze_text'),
    path('keywords/', views.keyword_list, name='keyword_list'),
    path('keywords/add/', views.add_keyword, name='add_keyword'),
    path('keywords/<int:pk>/delete/', views.delete_keyword, name='delete_keyword'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/create/', views.create_report, name='create_report'),
    path('reports/<int:pk>/', views.view_report, name='view_report'),
    path('reports/<int:pk>/delete/', views.delete_report, name='delete_report'),
] 