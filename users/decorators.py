from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to access this page.')
                return redirect('login')
            
            if not hasattr(request.user, 'userprofile'):
                messages.error(request, 'User profile not found.')
                return redirect('login')
            
            if request.user.userprofile.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                raise PermissionDenied('You do not have permission to access this page.')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    return role_required(['admin'])(view_func)

def analyst_required(view_func):
    return role_required(['admin', 'data_analyst'])(view_func)

def researcher_required(view_func):
    return role_required(['admin', 'researcher'])(view_func)

def marketer_required(view_func):
    return role_required(['admin', 'marketer'])(view_func)

def advanced_features_required(view_func):
    return role_required(['admin', 'data_analyst', 'researcher'])(view_func)

def report_access_required(view_func):
    return role_required(['admin', 'data_analyst', 'researcher'])(view_func)

def admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'userprofile'):
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        if request.user.userprofile.is_admin:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap

def analyst_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'userprofile'):
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        if request.user.userprofile.is_analyst:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap

def marketer_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'userprofile'):
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        if request.user.userprofile.is_marketer:
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap 