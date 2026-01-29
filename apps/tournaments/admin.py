"""
Admin configuration for tournaments.
"""

from django.contrib import admin

from .models import Tournament, Match


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    """Admin interface for Tournament model."""

    list_display = ['name', 'start_date', 'end_date', 'location', 'status', 'player_count']
    list_filter = ['status', 'start_date']
    search_fields = ['name', 'location']
    date_hierarchy = 'start_date'
    filter_horizontal = ['players', 'referees']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """Admin interface for Match model."""

    list_display = ['tournament', 'player1', 'player2', 'referee', 'round', 'status', 'scheduled_time']
    list_filter = ['status', 'round', 'tournament']
    search_fields = ['tournament__name', 'player1__username', 'player2__username']
    raw_id_fields = ['tournament', 'player1', 'player2', 'referee', 'winner']
