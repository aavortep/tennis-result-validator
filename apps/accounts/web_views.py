<<<<<<< HEAD
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
=======
"""
Template-based views for accounts.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
>>>>>>> main

from .models import User
from .services import AccountService


def register_view(request):
<<<<<<< HEAD
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role", "SPECTATOR")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")

        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return render(request, "accounts/register.html", {"form": request.POST})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "accounts/register.html", {"form": request.POST})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "accounts/register.html", {"form": request.POST})
=======
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'SPECTATOR')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return render(request, 'accounts/register.html', {'form': request.POST})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'accounts/register.html', {'form': request.POST})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'accounts/register.html', {'form': request.POST})
>>>>>>> main

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                role=role,
                first_name=first_name,
<<<<<<< HEAD
                last_name=last_name,
            )
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("home")
        except Exception as e:
            messages.error(request, str(e))

    return render(request, "accounts/register.html", {"form": {}})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
=======
                last_name=last_name
            )
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'accounts/register.html', {'form': {}})


def login_view(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
>>>>>>> main
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
<<<<<<< HEAD
            next_url = request.GET.get("next", "home")
=======
            next_url = request.GET.get('next', 'home')
>>>>>>> main
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

<<<<<<< HEAD
    return render(request, "accounts/login.html", {})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect("home")
=======
    return render(request, 'accounts/login.html', {})


def logout_view(request):
    """User logout."""
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect('home')
>>>>>>> main


@login_required
def profile_view(request):
<<<<<<< HEAD
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        user.phone = request.POST.get("phone", "")
        user.bio = request.POST.get("bio", "")
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "accounts/profile.html", {})
=======
    """User profile page."""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.bio = request.POST.get('bio', '')
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'accounts/profile.html', {})
>>>>>>> main


@login_required
def delete_account_view(request):
<<<<<<< HEAD
    if request.method == "POST":
=======
    """Delete user account."""
    if request.method == 'POST':
>>>>>>> main
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
<<<<<<< HEAD
        return redirect("home")

    return redirect("profile")
=======
        return redirect('home')

    return redirect('profile')
>>>>>>> main
