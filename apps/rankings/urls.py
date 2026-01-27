from django.urls import path

from . import views

app_name = 'rankings'

urlpatterns = [
    path('tournament/<int:tournament_id>/', views.TournamentLeaderboardView.as_view(), name='tournament-leaderboard'),
    path('global/', views.GlobalLeaderboardView.as_view(), name='global-leaderboard'),

    path('my/', views.MyRankingsView.as_view(), name='my-rankings'),
    path('my/global/', views.MyGlobalRankingView.as_view(), name='my-global-ranking'),
    path('player/<int:player_id>/', views.PlayerRankingsView.as_view(), name='player-rankings'),

    path('<int:pk>/', views.RankingDetailView.as_view(), name='ranking-detail'),

    path('tournament/<int:tournament_id>/initialize/', views.InitializeTournamentRankingsView.as_view(), name='initialize-rankings'),
    path('tournament/<int:tournament_id>/recalculate/', views.RecalculateRankingsView.as_view(), name='recalculate-rankings'),
]
