from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from apps.scores import web_views as scores_views

urlpatterns = [
    # Scores
    path('matches/<int:match_id>/score/', scores_views.score_submit, name='score_submit'),
    path('scores/<int:pk>/confirm/', scores_views.score_confirm, name='score_confirm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
