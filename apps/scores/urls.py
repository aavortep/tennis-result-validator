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
    path('disputes/create/', views.DisputeCreateView.as_view(), name='dispute-create'),
    path('disputes/<int:pk>/resolve/', views.DisputeResolveView.as_view(), name='dispute-resolve'),
    path('disputes/<int:pk>/review/', views.DisputeReviewView.as_view(), name='dispute-review'),
    path('disputes/<int:pk>/evidence/', views.DisputeEvidenceView.as_view(), name='dispute-evidence'),

    # Evidence endpoints
    path('evidence/submit/', views.EvidenceCreateView.as_view(), name='evidence-submit'),
]
