import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.utils.decorators import role_required
from .models import CustomUser

# Login view
# def login_view(request):
    # if request.method == "POST":
    #     username_or_email = request.POST.get("email")
    #     password = request.POST.get("password")

    #     user = authenticate(request, username=username_or_email, password=password)
        
    #     if user is not None:
    #         if user.is_active:
    #             if user:
    #                 login(request, user)
    #                 return redirect("dashboard")
    #             # Redirect by role
    #             if user.is_superuser or user.is_staff:
    #                 return redirect("/dashboard/")
    #             elif user.role == "set":
    #                 return redirect("set.index")
    #             elif user.role == "het":
    #                 return redirect("het.index")
    #             elif user.role == "training":
    #                 return redirect("training.index")
    #             else:
    #                 return redirect("access_denied")
    #         else:
    #             messages.error(request, "Your account is inactive.")
    #     else:
    #         messages.error(request, "Invalid username or password.")
    # return render(request, "pages/login.html")
def login_view(request):

    # 🔥 1. Already logged-in user → Auto redirect by role
    if request.user.is_authenticated:
        user = request.user
        if user.is_superuser or user.is_staff:
            return redirect("/dashboard/")
        elif user.role == "set":
            return redirect("set.index")
        elif user.role == "het":
            return redirect("het.index")
        elif user.role == "training":
            return redirect("training.index")
        else:
            return redirect("access_denied")

    # 🔥 2. Normal login POST
    if request.method == "POST":
        username_or_email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=username_or_email, password=password)

        if user:
            if not user.is_active:
                messages.error(request, "Your account is inactive.")
                return render(request, "pages/login.html")

            login(request, user)

            # 🔥 3. Redirect based on role
            if user.is_superuser or user.is_staff:
                return redirect("/dashboard/")
            elif user.role == "set":
                return redirect("set.index")
            elif user.role == "het":
                return redirect("het.index")
            elif user.role == "training":
                return redirect("training.index")
            else:
                return redirect("access_denied")

        else:
            messages.error(request, "Invalid username or password.")

    # 🔥 4. GET request → Show login page
    return render(request, "pages/login.html")

# Logout view
@login_required(login_url="login")
def logout_view(request):
    """Logout the user and redirect to login page"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

# Add user view
@login_required(login_url="login")
@role_required("admin")
def add_user(request):
    roles = CustomUser.ROLE_CHOICES
    form_data = request.POST or None
    context = {
        "roles": roles,
        "form_data": form_data,
    }
    """Only admin can create new users"""
    if request.method == "POST":
        full_name = request.POST.get("name")
        email = request.POST.get("email")
        role = request.POST.get("role")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        is_active = request.POST.get("is_active") == "on"

        # Password check
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            context = {
                "roles": roles,
                "form_data": form_data,
            }
            return render(request, "pages/admin/add-user.html", context)

        # Duplicate email check
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            context = {
                "roles": roles,
                "form_data": form_data,
            }
            return render(request, "pages/admin/add-user.html", context)

        # Create user
        CustomUser.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            is_active=is_active,
        )
        messages.success(request, f"User '{full_name}' created successfully!")
        return redirect("admin.users")

    return render(request, "pages/admin/add-user.html", context)


# Edit user view
@login_required(login_url="login")
@role_required("admin")
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    roles = CustomUser.ROLE_CHOICES

    if request.method == "POST":
        user.full_name = request.POST.get("name")
        user.email = request.POST.get("email")
        user.role = request.POST.get("role")
        user.is_active = request.POST.get("is_active") == "on"
        user.save()
        messages.success(request, f"User '{user.full_name}' updated successfully!")
        return redirect("admin.users")

    return render(request, "pages/admin/edit-user.html", {"user": user, "roles": roles})

# Delete user view
@login_required(login_url="login")
@role_required("admin")
def delete_user(request, user_id):
    """Only admin can delete users"""
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully!")
        return redirect("admin.users")

    return render(request, "pages/admin/delete-user.html", {"user": user})

# Change user password view
@login_required(login_url="login")
@role_required("admin")
def change_user_password(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not new_password or not confirm_password:
            messages.error(request, "Please fill in all fields.")
            return render(request, "pages/admin/change-password.html", {"user": user})

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "pages/admin/change-password.html", {"user": user})

        #  Update password securely
        user.set_password(new_password)
        user.save()

        messages.success(request, f"Password changed successfully for {user.full_name}.")
        return redirect("admin.users")

    return render(request, "pages/admin/change-password.html", {"user": user})