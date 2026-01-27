from django.urls import path

from . import views

app_name = 'scores'

urlpatterns = [
    # Score endpoints
    path('submit/', views.ScoreSubmitView.as_view(), name='score-submit'),
    path('<int:pk>/', views.ScoreDetailView.as_view(), name='score-detail'),
    path('<int:pk>/confirm/', views.ScoreConfirmView.as_view(), name='score-confirm'),
    path('match/<int:match_id>/', views.MatchScoresView.as_view(), name='match-scores'),

    # Dispute endpoints
    path('disputes/', views.DisputeListView.as_view(), name='dispute-list'),
    path('disputes/open/', views.OpenDisputesView.as_view(), name='open-disputes'),
    path('disputes/<int:pk>/', views.DisputeDetailView.as_view(), name='dispute-detail'),
]
