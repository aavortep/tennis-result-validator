from django.conf import settings
from django.db import models

from core.mixins import TimestampMixin


class Ranking(TimestampMixin):
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rankings"
    )
    tournament = models.ForeignKey(
        "tournaments.Tournament", on_delete=models.CASCADE, related_name="rankings"
    )
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    sets_won = models.IntegerField(default=0)
    sets_lost = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "rankings"
        ordering = ["position", "-points"]
        unique_together = ["player", "tournament"]

    def __str__(self):
        return f"{self.player.username} - {self.tournament.name}: #{self.position}"

    @property
    def matches_played(self):
        return self.wins + self.losses

    @property
    def win_percentage(self):
        if self.matches_played == 0:
            return 0.0
        return (self.wins / self.matches_played) * 100


class GlobalRanking(TimestampMixin):
    player = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="global_ranking",
    )
    total_points = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    tournaments_played = models.IntegerField(default=0)
    tournaments_won = models.IntegerField(default=0)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "global_rankings"
        ordering = ["position", "-total_points"]

    def __str__(self):
        return f"{self.player.username}: Global #{self.position}"
