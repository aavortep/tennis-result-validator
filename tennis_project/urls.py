"""
URL configuration for Tennis Tournament project.

Part B: Tournament & Match Orchestration
Builds on Part A (Accounts)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

from apps.accounts import web_views as accounts_views
from apps.tournaments import web_views as tournaments_views


def home(request):
    """Home page view."""
    return render(request, 'home.html')


urlpatterns = [
    # Home
    path('', home, name='home'),

    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/accounts/', include('apps.accounts.urls')),      # Part A
    path('api/tournaments/', include('apps.tournaments.urls')), # Part B

    # Template-based views - Accounts (Part A)
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('register/', accounts_views.register_view, name='register'),
    path('profile/', accounts_views.profile_view, name='profile'),

    # Template-based views - Tournaments (Part B)
    path('tournaments/', tournaments_views.tournament_list, name='tournament_list'),
    path('tournaments/create/', tournaments_views.tournament_create, name='tournament_create'),
    path('tournaments/<int:pk>/', tournaments_views.tournament_detail, name='tournament_detail'),
    path('tournaments/<int:pk>/edit/', tournaments_views.tournament_edit, name='tournament_edit'),
    path('tournaments/<int:pk>/add-player/', tournaments_views.tournament_add_player, name='tournament_add_player'),
    path('tournaments/<int:pk>/remove-player/<int:player_id>/', tournaments_views.tournament_remove_player, name='tournament_remove_player'),
    path('tournaments/<int:pk>/add-referee/', tournaments_views.tournament_add_referee, name='tournament_add_referee'),

    # Template-based views - Matches (Part B)
    path('matches/', tournaments_views.my_matches, name='my_matches'),
    path('matches/<int:pk>/', tournaments_views.match_detail, name='match_detail'),
    path('tournaments/<int:tournament_id>/matches/create/', tournaments_views.match_create, name='match_create'),
    path('matches/<int:pk>/edit/', tournaments_views.match_edit, name='match_edit'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
