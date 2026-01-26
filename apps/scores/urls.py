from django.urls import path

from . import views

app_name = 'scores'

urlpatterns = [
    # Score endpoints
    path('submit/', views.ScoreSubmitView.as_view(), name='score-submit'),
]
