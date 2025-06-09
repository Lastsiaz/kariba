from django.urls import path
from . import views

app_name = 'sentiment_analytics'

urlpatterns = [
    path('', views.sentiment_dashboard, name='dashboard'),
    path('analyze/', views.analyze_text, name='analyze'),
    path('save-training-data/', views.save_training_data, name='save_training_data'),
    path('test-ml/', views.test_ml_model, name='test_ml'),
    path('model-info/', views.model_info, name='model_info'),
    path('map/', views.sentiment_map, name='map'),
    path('trends/', views.sentiment_trends, name='trends'),
    path('report/', views.generate_report, name='generate_report'),
] 