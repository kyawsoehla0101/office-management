# accounts/utils/decorators.py
from functools import wraps
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def role_required(*allowed_roles):
    """
    Check if user has one of the allowed roles.
    Example: @role_required('ADMIN', 'SET')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            user_role = getattr(user, "role", None)

            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # unauthorized
            messages.error(request, "You do not have permission to access this page.")
            return render(request, "pages/admin/access-denied.html")

        return _wrapped_view
    return decorator
