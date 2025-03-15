from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash, login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta
from .forms import (
    UserRegistrationForm, UserProfileUpdateForm, AdminUserRegistrationForm, UserUpdateForm
)
from .models import UserProfile
from .decorators import admin_required, analyst_required, role_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import ensure_csrf_cookie

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
    if not request.user.userprofile.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'User registered successfully!')
            return redirect('user_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/admin_register_user.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileUpdateForm(request.POST, instance=request.user.userprofile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
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
    if not request.user.userprofile.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    users = UserProfile.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
def edit_user(request, user_id):
    if not request.user.userprofile.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    user_profile = UserProfile.objects.get(id=user_id)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user_profile.user)
        p_form = UserProfileUpdateForm(request.POST, instance=user_profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('user_list')
    else:
        u_form = UserUpdateForm(instance=user_profile.user)
        p_form = UserProfileUpdateForm(instance=user_profile)
    return render(request, 'users/edit_user.html', {'u_form': u_form, 'p_form': p_form, 'user_profile': user_profile})

@login_required
def delete_user(request, user_id):
    if not request.user.userprofile.is_admin:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    user_profile = UserProfile.objects.get(id=user_id)
    if request.method == 'POST':
        user_profile.user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('user_list')
    return render(request, 'users/delete_user.html', {'user_profile': user_profile})

@login_required
def dashboard(request):
    user_profile = request.user.userprofile
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def analysis(request):
    if not request.user.userprofile.is_analyst:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    return render(request, 'users/analysis.html')

@login_required
def reports(request):
    if not request.user.userprofile.is_analyst:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    return render(request, 'users/reports.html')

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

def logout_view(request):
    # Logout the user
    logout(request)
    
    # Clear the session
    request.session.flush()
    
    # Add success message
    messages.success(request, 'You have been logged out successfully.')
    
    # Redirect to login page
    return redirect('login')