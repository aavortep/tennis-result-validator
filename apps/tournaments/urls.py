"""
URL patterns for tournaments app.
"""

from django.urls import path

from . import views

app_name = 'tournaments'

urlpatterns = [
    # Tournament endpoints
    path('', views.TournamentListCreateView.as_view(), name='tournament-list'),
    path('<int:pk>/', views.TournamentDetailView.as_view(), name='tournament-detail'),
    path('<int:pk>/add-player/', views.TournamentAddPlayerView.as_view(), name='add-player'),
    path('<int:pk>/remove-player/<int:player_id>/', views.TournamentRemovePlayerView.as_view(), name='remove-player'),
    path('<int:pk>/add-referee/', views.TournamentAddRefereeView.as_view(), name='add-referee'),
    path('<int:pk>/status/', views.TournamentStatusView.as_view(), name='tournament-status'),
    path('<int:pk>/matches/', views.TournamentMatchesView.as_view(), name='tournament-matches'),

    # Match endpoints
    path('matches/', views.MatchListCreateView.as_view(), name='match-list'),
    path('matches/<int:pk>/', views.MatchDetailView.as_view(), name='match-detail'),
    path('matches/my-matches/', views.MyMatchesView.as_view(), name='my-matches'),
    path('matches/<int:pk>/assign-players/', views.MatchAssignPlayersView.as_view(), name='assign-players'),
    path('matches/<int:pk>/assign-referee/', views.MatchAssignRefereeView.as_view(), name='assign-referee'),
    path('matches/<int:pk>/start/', views.MatchStartView.as_view(), name='start-match'),
]
