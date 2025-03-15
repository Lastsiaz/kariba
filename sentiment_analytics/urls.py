from django.urls import path
from . import views

app_name = 'sentiment_analytics'

urlpatterns = [
    path('', views.sentiment_dashboard, name='dashboard'),
    path('analyze/', views.analyze_text, name='analyze'),
    path('map/', views.sentiment_map, name='map'),
    path('trends/', views.sentiment_trends, name='trends'),
    path('report/', views.generate_report, name='generate_report'),
] 