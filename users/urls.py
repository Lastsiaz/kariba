from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('admin/register/', views.admin_register_user, name='admin_register_user'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('users/', views.user_list, name='user_list'),
    path('user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('researcher/dashboard/', views.researcher_dashboard, name='researcher_dashboard'),
    path('marketer/dashboard/', views.marketer_dashboard, name='marketer_dashboard'),
    path('analyst/dashboard/', views.analyst_dashboard, name='analyst_dashboard'),
    path('analysis/', views.analysis, name='analysis'),
    path('reports/', views.reports, name='reports'),
    path('campaign/', views.campaign, name='campaign'),
    path('all-reports/', views.all_reports, name='all_reports'),
    path('report/<int:report_id>/view/', views.view_report, name='view_report'),
    path('report/<int:report_id>/edit/', views.edit_report, name='edit_report'),
    path('check-new-reports/', views.check_new_reports, name='check_new_reports'),
    
    # Password Reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    
    # Password Change URLs
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),
] 