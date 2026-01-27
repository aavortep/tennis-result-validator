"""
URL configuration for Tennis Tournament project.

Part A: Foundation - Authentication & User Management
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

from apps.accounts import web_views as accounts_views


def home(request):
    """Home page view."""
    return render(request, 'home.html')


urlpatterns = [
    # Home
    path('', home, name='home'),

    # Admin
    path('admin/', admin.site.urls),

    # API endpoints - Part A: Accounts
    path('api/accounts/', include('apps.accounts.urls')),

    # Template-based views - Accounts
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('register/', accounts_views.register_view, name='register'),
    path('profile/', accounts_views.profile_view, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
