from django.contrib import admin

from .models import GlobalRanking, Ranking


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ["player", "tournament", "position", "points", "wins", "losses"]
    list_filter = ["tournament", "position"]
    search_fields = ["player__username", "tournament__name"]
    ordering = ["tournament", "position"]
    raw_id_fields = ["player", "tournament"]


@admin.register(GlobalRanking)
class GlobalRankingAdmin(admin.ModelAdmin):
    list_display = [
        "player",
        "position",
        "total_points",
        "total_wins",
        "tournaments_won",
    ]
    list_filter = ["position"]
    search_fields = ["player__username"]
    ordering = ["position"]
    raw_id_fields = ["player"]
