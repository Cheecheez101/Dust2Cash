from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def agent_required(view_func):
    """Decorator to ensure only users with an agent profile can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first')
            return redirect('login')
        
        try:
            agent_profile = request.user.agent_profile
        except Exception:
            messages.error(request, 'You do not have agent access')
            return redirect('client_dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def client_required(view_func):
    """Decorator to ensure only users with a client profile can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first')
            return redirect('login')
        
        try:
            client_profile = request.user.client_profile
        except Exception:
            messages.error(request, 'You need to complete your profile first')
            return redirect('client_profile')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to ensure only staff users can access the view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first')
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, 'You do not have admin access')
            return redirect('landing')
        return view_func(request, *args, **kwargs)
    return wrapper
