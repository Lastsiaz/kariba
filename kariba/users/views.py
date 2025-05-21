from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash, login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.sessions.exceptions import SessionInterrupted
from django.views.decorators.http import require_http_methods
from .forms import (
    UserRegistrationForm, UserProfileUpdateForm, AdminUserRegistrationForm, UserUpdateForm
)
from .models import UserProfile, Campaign, Report
from .decorators import admin_required, analyst_required, role_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
import psutil
import platform
from datetime import datetime
from django.urls import reverse
import csv
import io
import json
import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
@admin_required
def admin_register_user(request):
    if request.method == 'POST':
        form = AdminUserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    
                    # Get the user profile
                    user_profile = UserProfile.objects.get(user=user)
                    
                    # Ensure department matches role
                    role = user_profile.role
                    if role == 'admin' and user_profile.department != 'Administration':
                        user_profile.department = 'Administration'
                        user_profile.save()
                    elif role == 'analyst' and user_profile.department != 'Data Analytics':
                        user_profile.department = 'Data Analytics'
                        user_profile.save()
                    elif role == 'marketer' and user_profile.department != 'Marketing':
                        user_profile.department = 'Marketing'
                        user_profile.save()
                    elif role == 'researcher' and user_profile.department != 'Research':
                        user_profile.department = 'Research'
                        user_profile.save()
                    elif role == 'general_user' and user_profile.department != 'General':
                        user_profile.department = 'General'
                        user_profile.save()
                    
                    messages.success(request, 'User registered successfully!')
                    return redirect('user_list')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminUserRegistrationForm()
    return render(request, 'users/admin_register_user.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        
        if u_form.is_valid() and p_form.is_valid():
            try:
                # Save user form
                u_form.save()
                
                # Handle profile picture
                profile = p_form.save(commit=False)
                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']
                    print(f"Profile picture received: {profile.profile_picture.name}")  # Debug print
                profile.save()
                
                messages.success(request, 'Your profile has been updated!')
                return redirect('profile')
            except Exception as e:
                print(f"Error saving profile: {str(e)}")  # Debug print
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            print(f"Form errors: {p_form.errors}")  # Debug print
            messages.error(request, 'Please correct the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileUpdateForm(instance=request.user.userprofile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user': request.user,
        'profile': request.user.userprofile
    }
    return render(request, 'users/profile.html', context)

@login_required
@admin_required
def user_list(request):
    # Get all users with their profiles
    users = UserProfile.objects.all().select_related('user')
    
    # Ensure all users have the correct department based on their role
    for profile in users:
        if profile.role == 'admin' and profile.department != 'Administration':
            profile.department = 'Administration'
            profile.save()
        elif profile.role == 'analyst' and profile.department != 'Data Analytics':
            profile.department = 'Data Analytics'
            profile.save()
        elif profile.role == 'marketer' and profile.department != 'Marketing':
            profile.department = 'Marketing'
            profile.save()
        elif profile.role == 'researcher' and profile.department != 'Research':
            profile.department = 'Research'
            profile.save()
        elif profile.role == 'general_user' and profile.department != 'General':
            profile.department = 'General'
            profile.save()
    
    # Refresh the users list after updates
    users = UserProfile.objects.all().select_related('user')
    
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@admin_required
def edit_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        # Get or create UserProfile
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'general_user',
                'department': 'General'
            }
        )
        
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=user)
            p_form = UserProfileUpdateForm(request.POST, instance=user_profile)
            
            if u_form.is_valid() and p_form.is_valid():
                with transaction.atomic():
                    # Save user data
                    u_form.save()
                    
                    # Save profile data
                    profile = p_form.save(commit=False)
                    
                    # Ensure department matches role
                    role = p_form.cleaned_data['role']
                    if role == 'admin':
                        profile.department = 'Administration'
                    elif role == 'analyst':
                        profile.department = 'Data Analytics'
                    elif role == 'marketer':
                        profile.department = 'Marketing'
                    elif role == 'researcher':
                        profile.department = 'Research'
                    else:
                        profile.department = 'General'
                    
                    # Save the profile with the updated department
                    profile.save()
                    
                    # Save profile picture if provided
                    if 'profile_picture' in request.FILES:
                        profile.profile_picture = request.FILES['profile_picture']
                        profile.save()
                
                messages.success(request, 'User updated successfully!')
                return redirect('user_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            u_form = UserUpdateForm(instance=user)
            p_form = UserProfileUpdateForm(instance=user_profile)
        
        context = {
            'u_form': u_form,
            'p_form': p_form,
            'user_profile': user_profile
        }
        return render(request, 'users/edit_user.html', context)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('user_list')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('user_list')

@login_required
@admin_required
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if user == request.user:
            messages.error(request, 'You cannot delete your own account.')
            return redirect('user_list')
            
        if request.method == 'POST':
            try:
                with transaction.atomic():
                    # Delete related UserProfile first
                    if hasattr(user, 'userprofile'):
                        user.userprofile.delete()
                    
                    # Delete the user
                    user.delete()
                    
                messages.success(request, 'User deleted successfully!')
                return redirect('user_list')
            except Exception as e:
                messages.error(request, f'Error deleting user: {str(e)}')
                return redirect('user_list')
            
        # For GET request, show confirmation page
        return render(request, 'users/delete_user.html', {'user': user})
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('user_list')
    except Exception as e:
        messages.error(request, f'Error deleting user: {str(e)}')
        return redirect('user_list')

@login_required
def dashboard(request):
    user_profile = request.user.userprofile
    
    # Debug print to check role and department
    print(f"User role: {user_profile.role}, Department: {user_profile.department}")
    
    # Ensure department matches role
    if user_profile.role == 'admin' and user_profile.department != 'Administration':
        user_profile.department = 'Administration'
        user_profile.save()
    elif user_profile.role == 'analyst' and user_profile.department != 'Data Analytics':
        user_profile.department = 'Data Analytics'
        user_profile.save()
    elif user_profile.role == 'marketer' and user_profile.department != 'Marketing':
        user_profile.department = 'Marketing'
        user_profile.save()
    elif user_profile.role == 'researcher' and user_profile.department != 'Research':
        user_profile.department = 'Research'
        user_profile.save()
    elif user_profile.role == 'general_user' and user_profile.department != 'General':
        user_profile.department = 'General'
        user_profile.save()
    
    # Get user's display name
    user_display_name = request.user.get_full_name() or request.user.username
    
    # Redirect based on role
    if user_profile.role == 'admin':
        # Admin dashboard data
        total_users = User.objects.count()
        
        # Ensure all users have the correct department based on their role
        all_profiles = UserProfile.objects.all()
        for profile in all_profiles:
            if profile.role == 'admin' and profile.department != 'Administration':
                profile.department = 'Administration'
                profile.save()
            elif profile.role == 'analyst' and profile.department != 'Data Analytics':
                profile.department = 'Data Analytics'
                profile.save()
            elif profile.role == 'marketer' and profile.department != 'Marketing':
                profile.department = 'Marketing'
                profile.save()
            elif profile.role == 'researcher' and profile.department != 'Research':
                profile.department = 'Research'
                profile.save()
            elif profile.role == 'general_user' and profile.department != 'General':
                profile.department = 'General'
                profile.save()
        
        # Count users by role after ensuring departments are correct
        total_analysts = UserProfile.objects.filter(role='analyst').count()
        total_marketers = UserProfile.objects.filter(role='marketer').count()
        total_researchers = UserProfile.objects.filter(role='researcher').count()
        
        # System performance metrics
        boot_time = timezone.make_aware(datetime.fromtimestamp(psutil.boot_time()))
        uptime = timezone.now() - boot_time
        system_uptime = f"{uptime.days}d {uptime.seconds//3600}h"
        
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # Get active users (users who logged in in the last 24 hours)
        active_users = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=1)
        ).count()
        
        # Get recent reports
        recent_reports = Report.objects.all().order_by('-created_at')[:5]
        
        # Get recent activities
        recent_activities = []
        
        # Add system initialization activity
        recent_activities.append({
            'user': 'System',
            'action': 'System initialized',
            'action_type': 'system',
            'time': boot_time,
            'status': 'completed'
        })
        
        # Add user login activities
        recent_logins = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=1)
        ).order_by('-last_login')
        
        for user_obj in recent_logins:
            recent_activities.append({
                'user': user_obj,
                'action': 'Logged in',
                'time': user_obj.last_login,
                'status': 'completed'
            })
        
        # Sort activities by time and limit to 5 most recent
        recent_activities.sort(key=lambda x: x['time'], reverse=True)
        recent_activities = recent_activities[:5]
        
        context = {
            'total_users': total_users,
            'total_analysts': total_analysts,
            'total_marketers': total_marketers,
            'total_researchers': total_researchers,
            'system_uptime': system_uptime,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage,
            'active_users': active_users,
            'recent_reports': recent_reports,
            'recent_activities': recent_activities,
            'user_display_name': user_display_name,
        }
        return render(request, 'users/admin_dashboard.html', context)
    elif user_profile.role == 'researcher':
        return redirect('researcher_dashboard')
    elif user_profile.role == 'analyst':
        return redirect('analyst_dashboard')
    elif user_profile.role == 'marketer':
        return redirect('marketer_dashboard')
    else:
        # Default dashboard for other users
        # Get basic stats for the default dashboard
        total_analyses = Report.objects.filter(
            created_by=request.user
        ).count()
        
        # Calculate average sentiment (placeholder)
        avg_sentiment = 0.75
        
        # Get analyses done today
        analyses_today = Report.objects.filter(
            created_by=request.user,
            created_at__date=timezone.now().date()
        ).count()
        
        context = {
            'total_analyses': total_analyses,
            'avg_sentiment': avg_sentiment,
            'analyses_today': analyses_today,
            'user_display_name': user_display_name,
        }
        return render(request, 'dashboard.html', context)

@login_required
@role_required(['analyst'])
def analyst_dashboard(request):
    user_profile = request.user.userprofile
    
    # Get user's display name
    user_display_name = request.user.get_full_name() or request.user.username
    
    # Get analysis statistics
    total_analyses = Report.objects.filter(
        author=request.user,
        report_type='analysis'
    ).count()
    
    total_reports = Report.objects.filter(
        author=request.user
    ).count()
    
    total_sources = Campaign.objects.filter(
        created_by=request.user,
        campaign_type='survey'
    ).count()
    
    active_projects = Campaign.objects.filter(
        created_by=request.user,
        status='active'
    ).count()
    
    # Get user's reports
    reports = Report.objects.filter(author=request.user).order_by('-created_at')
    
    context = {
        'user_profile': user_profile,
        'user_display_name': user_display_name,
        'total_analyses': total_analyses,
        'total_reports': total_reports,
        'total_sources': total_sources,
        'active_projects': active_projects,
        'reports': reports,
    }
    
    return render(request, 'users/analyst_dashboard.html', context)

@login_required
@role_required(['analyst', 'marketer'])
def analysis(request):
    if request.method == 'POST':
        try:
            # Get form data
            analysis_name = request.POST.get('analysis_name')
            analysis_type = request.POST.get('analysis_type')
            data_source = request.POST.get('data_source')
            date_range = request.POST.get('date_range')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Here you would typically create a new analysis record in your database
            # For now, we'll just return a success response
            return JsonResponse({
                'success': True,
                'message': 'Analysis created successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    # GET request - show the analysis page
    return render(request, 'users/analysis.html')

@login_required
@role_required(['analyst', 'marketer', 'researcher'])
def reports(request):
    return render(request, 'users/reports.html')

@login_required
def campaign(request):
    if request.method == 'POST':
        try:
            campaign = Campaign.objects.create(
                name=request.POST.get('campaignName'),
                description=request.POST.get('campaignDescription'),
                campaign_type=request.POST.get('campaignType'),
                start_date=request.POST.get('startDate'),
                end_date=request.POST.get('endDate'),
                created_by=request.user,
                status='draft'
            )
            messages.success(request, 'Campaign created successfully!')
            return redirect('campaign')
        except Exception as e:
            messages.error(request, f'Error creating campaign: {str(e)}')
            return redirect('campaign')

    # Get campaigns for the current user
    campaigns = Campaign.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Calculate statistics
    total_campaigns = campaigns.count()
    active_campaigns = campaigns.filter(status='active').count()
    completed_campaigns = campaigns.filter(status='completed').count()
    
    # Calculate success rate (placeholder - you can implement your own logic)
    success_rate = 0
    if completed_campaigns > 0:
        successful_campaigns = campaigns.filter(status='completed', success_metrics__gt=0).count()
        success_rate = round((successful_campaigns / completed_campaigns) * 100)

    context = {
        'campaigns': campaigns,
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'completed_campaigns': completed_campaigns,
        'success_rate': success_rate,
    }
    
    return render(request, 'users/campaign.html', context)

@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@require_http_methods(["POST"])
def logout_view(request):
    try:
        # First, logout the user
        logout(request)
        
        # Clear the session without saving
        request.session.clear()
        
        # Add success message
        messages.success(request, 'You have been logged out successfully.')
    except Exception as e:
        # Log the error but still proceed with logout
        print(f"Error during logout: {str(e)}")
    
    # Redirect to login page
    return redirect('login')

@login_required
@admin_required
def all_reports(request):
    """View for displaying all reports with filtering options."""
    # Get filter parameters from request
    report_type = request.GET.get('type')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Start with all reports
    reports = Report.objects.all()
    
    # Apply filters if provided
    if report_type:
        reports = reports.filter(report_type=report_type)
    if status:
        reports = reports.filter(status=status)
    if date_from:
        reports = reports.filter(created_at__gte=date_from)
    if date_to:
        reports = reports.filter(created_at__lte=date_to)
    
    # Order by most recent first
    reports = reports.order_by('-created_at')
    
    context = {
        'reports': reports,
        'report_types': Report.TYPE_CHOICES,
        'status_choices': Report.STATUS_CHOICES,
        'selected_type': report_type,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'users/all_reports.html', context)

@login_required
@role_required('researcher')
def researcher_dashboard(request):
    user_profile = request.user.userprofile
    
    # Get user's display name
    user_display_name = request.user.get_full_name() or request.user.username
    
    # Get research statistics
    active_projects = Campaign.objects.filter(
        created_by=request.user,
        status='active',
        campaign_type='survey'  # Filter for research/survey campaigns
    ).count()
    
    completed_projects = Campaign.objects.filter(
        created_by=request.user,
        status='completed',
        campaign_type='survey'  # Filter for research/survey campaigns
    ).count()
    
    total_reports = Report.objects.filter(
        author=request.user,
        report_type='research'  # Filter for research reports
    ).count()
    
    total_publications = Report.objects.filter(
        author=request.user,
        report_type='research'  # Filter for research reports
    ).count()
    
    # Get recent research projects
    recent_projects = Campaign.objects.filter(
        created_by=request.user,
        campaign_type='survey'  # Filter for research/survey campaigns
    ).order_by('-created_at')[:5]
    
    # Get recent publications
    recent_publications = Report.objects.filter(
        author=request.user,
        report_type='research'  # Filter for research reports
    ).order_by('-created_at')[:5]
    
    context = {
        'user_profile': user_profile,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_reports': total_reports,
        'total_publications': total_publications,
        'recent_projects': recent_projects,
        'recent_publications': recent_publications,
        'user_display_name': user_display_name,
    }
    
    return render(request, 'users/researcher_dashboard.html', context)

@login_required
@role_required(['analyst'])
def data_sources(request):
    # Get data sources (campaigns of type survey) for the current user
    data_sources = Campaign.objects.filter(
        created_by=request.user,
        campaign_type='survey'
    ).order_by('-created_at')
    
    context = {
        'data_sources': data_sources,
        'total_sources': data_sources.count(),
        'active_sources': data_sources.filter(status='active').count(),
        'completed_sources': data_sources.filter(status='completed').count(),
    }
    
    return render(request, 'users/data_sources.html', context)

@login_required
@role_required('marketer')
def marketer_dashboard(request):
    user_profile = request.user.userprofile
    
    # Get user's display name
    user_display_name = request.user.get_full_name() or request.user.username
    
    # Get marketing statistics
    total_campaigns = Campaign.objects.filter(
        created_by=request.user,
        campaign_type='marketing'
    ).count()
    
    active_campaigns = Campaign.objects.filter(
        created_by=request.user,
        campaign_type='marketing',
        status='active'
    ).count()
    
    completed_campaigns = Campaign.objects.filter(
        created_by=request.user,
        campaign_type='marketing',
        status='completed'
    ).count()
    
    # Get recent campaigns
    recent_campaigns = Campaign.objects.filter(
        created_by=request.user,
        campaign_type='marketing'
    ).order_by('-created_at')[:5]
    
    context = {
        'user_profile': user_profile,
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'completed_campaigns': completed_campaigns,
        'recent_campaigns': recent_campaigns,
        'user_display_name': user_display_name,
    }
    
    return render(request, 'users/marketer_dashboard.html', context)

@login_required
@role_required(['analyst', 'marketer', 'researcher'])
def view_report(request, report_id):
    """View a specific report."""
    report = get_object_or_404(Report, id=report_id)
    
    # Check if the user has permission to view this report
    if report.author != request.user and not request.user.userprofile.is_admin:
        raise PermissionDenied("You don't have permission to view this report.")
    
    context = {
        'report': report,
        'user_profile': request.user.userprofile,
    }
    
    return render(request, 'users/view_report.html', context)

@login_required
@role_required(['analyst', 'marketer', 'researcher'])
def edit_report(request, report_id):
    """Edit a specific report."""
    report = get_object_or_404(Report, id=report_id)
    
    # Check if the user has permission to edit this report
    if report.author != request.user and not request.user.userprofile.is_admin:
        raise PermissionDenied("You don't have permission to edit this report.")
    
    if request.method == 'POST':
        # Handle form submission for editing the report
        # This is a placeholder - you would need to implement the actual form handling
        messages.success(request, 'Report updated successfully!')
        return redirect('view_report', report_id=report.id)
    
    context = {
        'report': report,
        'user_profile': request.user.userprofile,
    }
    
    return render(request, 'users/edit_report.html', context)

@role_required(['admin', 'analyst', 'marketer', 'researcher'])
def check_new_reports(request):
    """Check for new reports and return them as JSON."""
    # Get reports created in the last 5 minutes
    five_minutes_ago = timezone.now() - timezone.timedelta(minutes=5)
    new_reports = Report.objects.filter(
        created_at__gte=five_minutes_ago,
        status='draft'  # Only get draft reports that need review
    ).order_by('-created_at')
    
    reports_data = []
    for report in new_reports:
        reports_data.append({
            'id': report.id,
            'title': report.title,
            'author': report.author.get_full_name() or report.author.username,
            'type': report.get_report_type_display(),
            'created_at': report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'url': reverse('view_report', args=[report.id])
        })
    
    return JsonResponse({
        'new_reports': reports_data,
        'count': len(reports_data)
    })

@login_required
@role_required(['analyst'])
def export_report(request):
    """Export reports in various formats."""
    try:
        # Get the format type from the query parameters
        format_type = request.GET.get('format', 'pdf').lower()
        
        # Get reports authored by the current user
        reports = Report.objects.filter(author=request.user).order_by('-created_at')
        
        if not reports.exists():
            messages.error(request, 'No reports found to export.')
            return redirect('analyst_dashboard')
        
        if format_type == 'pdf':
            try:
                # Create a PDF response
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="reports_export.pdf"'
                
                # Create the PDF document
                doc = SimpleDocTemplate(response, pagesize=letter)
                elements = []
                
                # Add title
                styles = getSampleStyleSheet()
                title_style = styles['Heading1']
                title = Paragraph("Reports Export", title_style)
                elements.append(title)
                elements.append(Paragraph("<br/><br/>", styles['Normal']))
                
                # Create table data
                data = [['Title', 'Type', 'Status', 'Created At']]
                for report in reports:
                    data.append([
                        report.title,
                        report.get_report_type_display(),
                        report.get_status_display(),
                        report.created_at.strftime('%Y-%m-%d %H:%M')
                    ])
                
                # Create table
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
                
                # Build PDF
                doc.build(elements)
                return response
            except Exception as e:
                messages.error(request, f'Error generating PDF file: {str(e)}')
                return redirect('analyst_dashboard')
            
        elif format_type == 'excel':
            try:
                # Create an Excel response
                output = io.BytesIO()
                workbook = xlsxwriter.Workbook(output)
                worksheet = workbook.add_worksheet()
                
                # Add title
                title_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14,
                    'align': 'center',
                    'bg_color': '#4F81BD',
                    'font_color': 'white',
                    'border': 1
                })
                
                worksheet.merge_range('A1:D1', 'Reports Export', title_format)
                
                # Add headers
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#B8CCE4',
                    'border': 1
                })
                
                headers = ['Title', 'Type', 'Status', 'Created At']
                for col_num, header in enumerate(headers):
                    worksheet.write(2, col_num, header, header_format)
                
                # Add data
                for row_num, report in enumerate(reports):
                    worksheet.write(row_num + 3, 0, report.title)
                    worksheet.write(row_num + 3, 1, report.get_report_type_display())
                    worksheet.write(row_num + 3, 2, report.get_status_display())
                    worksheet.write(row_num + 3, 3, report.created_at.strftime('%Y-%m-%d %H:%M'))
                
                # Adjust column widths
                worksheet.set_column(0, 0, 30)  # Title
                worksheet.set_column(1, 1, 15)  # Type
                worksheet.set_column(2, 2, 15)  # Status
                worksheet.set_column(3, 3, 20)  # Created At
                
                # Close the workbook
                workbook.close()
                
                # Get the value of the BytesIO buffer and write it to the response
                output.seek(0)
                response = HttpResponse(
                    output.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename="reports_export.xlsx"'
                return response
            except Exception as e:
                messages.error(request, f'Error generating Excel file: {str(e)}')
                return redirect('analyst_dashboard')
            
        elif format_type == 'csv':
            try:
                # Create a CSV response
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="reports_export.csv"'
                
                # Create a CSV writer
                writer = csv.writer(response)
                
                # Write the header row
                writer.writerow(['Title', 'Type', 'Status', 'Created At'])
                
                # Write the data rows
                for report in reports:
                    writer.writerow([
                        report.title,
                        report.get_report_type_display(),
                        report.get_status_display(),
                        report.created_at.strftime('%Y-%m-%d %H:%M')
                    ])
                
                return response
            except Exception as e:
                messages.error(request, f'Error generating CSV file: {str(e)}')
                return redirect('analyst_dashboard')
        
        else:
            messages.error(request, 'Invalid export format specified.')
            return redirect('analyst_dashboard')
            
    except Exception as e:
        messages.error(request, f'Error exporting reports: {str(e)}')
        return redirect('analyst_dashboard')

@login_required
@role_required(['analyst', 'marketer', 'researcher'])
def create_report(request):
    """Create a new report."""
    if request.method == 'POST':
        # Handle form submission for creating a new report
        title = request.POST.get('title')
        content = request.POST.get('content')
        report_type = request.POST.get('report_type')
        
        # Create the report
        report = Report.objects.create(
            title=title,
            content=content,
            report_type=report_type,
            author=request.user,
            status='draft'
        )
        
        messages.success(request, 'Report created successfully!')
        return redirect('view_report', report_id=report.id)
    
    # Get the user's display name
    user_display_name = request.user.get_full_name() or request.user.username
    
    context = {
        'user_profile': request.user.userprofile,
        'user_display_name': user_display_name,
        'report_types': Report.REPORT_TYPES,
    }
    
    return render(request, 'users/create_report.html', context)