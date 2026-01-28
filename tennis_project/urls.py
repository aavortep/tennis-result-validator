from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

from apps.accounts import web_views as accounts_views
from apps.scores import web_views as scores_views


def home(request):
    """Home page view."""
    return render(request, 'home.html')


urlpatterns = [
    # Home
    path('', home, name='home'),

    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/scores/', include('apps.scores.urls')),

    # Accounts
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('register/', accounts_views.register_view, name='register'),
    path('profile/', accounts_views.profile_view, name='profile'),

    # Scores
    path('matches/<int:match_id>/score/', scores_views.score_submit, name='score_submit'),
    path('scores/<int:pk>/confirm/', scores_views.score_confirm, name='score_confirm'),

    # Disputes
    path('disputes/', scores_views.dispute_list, name='dispute_list'),
    path('disputes/<int:pk>/', scores_views.dispute_detail, name='dispute_detail'),
    path('matches/<int:match_id>/dispute/', scores_views.dispute_create, name='dispute_create'),
    path('disputes/<int:pk>/resolve/', scores_views.dispute_resolve, name='dispute_resolve'),
    path('disputes/<int:dispute_id>/evidence/', scores_views.evidence_add, name='evidence_add'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
