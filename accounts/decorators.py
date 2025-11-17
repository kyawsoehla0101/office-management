from django.shortcuts import render
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    """Allow only admin role users (or Django superusers)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        
        if not (request.user.role == "admin" or request.user.is_superuser):
            messages.error(request, "You do not have permission to access this page.")
            return render(request, "pages/admin/access-denied.html", status=403)  # 👈 create this simple template
        return view_func(request, *args, **kwargs)
    return wrapper
