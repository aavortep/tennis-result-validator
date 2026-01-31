from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from apps.accounts import web_views as accounts_views
from apps.rankings import web_views as rankings_views
from apps.scores import web_views as scores_views
from apps.tournaments import web_views as tournaments_views


def home(request):
    return render(request, "home.html")


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/tournaments/", include("apps.tournaments.urls")),
    path("api/scores/", include("apps.scores.urls")),
    path("api/rankings/", include("apps.rankings.urls")),
    path("login/", accounts_views.login_view, name="login"),
    path("logout/", accounts_views.logout_view, name="logout"),
    path("register/", accounts_views.register_view, name="register"),
    path("profile/", accounts_views.profile_view, name="profile"),
    path("tournaments/", tournaments_views.tournament_list, name="tournament_list"),
    path(
        "tournaments/create/",
        tournaments_views.tournament_create,
        name="tournament_create",
    ),
    path(
        "tournaments/<int:pk>/",
        tournaments_views.tournament_detail,
        name="tournament_detail",
    ),
    path(
        "tournaments/<int:pk>/edit/",
        tournaments_views.tournament_edit,
        name="tournament_edit",
    ),
    path(
        "tournaments/<int:pk>/add-player/",
        tournaments_views.tournament_add_player,
        name="tournament_add_player",
    ),
    path(
        "tournaments/<int:pk>/remove-player/<int:player_id>/",
        tournaments_views.tournament_remove_player,
        name="tournament_remove_player",
    ),
    path(
        "tournaments/<int:pk>/add-referee/",
        tournaments_views.tournament_add_referee,
        name="tournament_add_referee",
    ),
    path("matches/", tournaments_views.my_matches, name="my_matches"),
    path("matches/<int:pk>/", tournaments_views.match_detail, name="match_detail"),
    path(
        "tournaments/<int:tournament_id>/matches/create/",
        tournaments_views.match_create,
        name="match_create",
    ),
    path("matches/<int:pk>/edit/", tournaments_views.match_edit, name="match_edit"),
    path(
        "matches/<int:match_id>/score/", scores_views.score_submit, name="score_submit"
    ),
    path("scores/<int:pk>/confirm/", scores_views.score_confirm, name="score_confirm"),
    path("disputes/", scores_views.dispute_list, name="dispute_list"),
    path("disputes/<int:pk>/", scores_views.dispute_detail, name="dispute_detail"),
    path(
        "matches/<int:match_id>/dispute/",
        scores_views.dispute_create,
        name="dispute_create",
    ),
    path(
        "disputes/<int:pk>/resolve/",
        scores_views.dispute_resolve,
        name="dispute_resolve",
    ),
    path(
        "disputes/<int:dispute_id>/evidence/",
        scores_views.evidence_add,
        name="evidence_add",
    ),
    path("rankings/", rankings_views.global_rankings, name="global_rankings"),
    path(
        "rankings/tournament/<int:tournament_id>/",
        rankings_views.tournament_rankings,
        name="tournament_rankings",
    ),
    path("rankings/my/", rankings_views.my_rankings, name="my_rankings"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
