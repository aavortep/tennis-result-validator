"""
Tournament and Match models.
"""

from django.db import models
from django.conf import settings

from core.mixins import TimestampMixin


class Tournament(TimestampMixin):
    """Tournament model representing a tennis tournament."""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        REGISTRATION = 'REGISTRATION', 'Registration Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    max_players = models.PositiveIntegerField(default=32)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tournaments'
    )
    players = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='tournaments',
        blank=True,
        limit_choices_to={'role': 'PLAYER'}
    )
    referees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='referee_tournaments',
        blank=True,
        limit_choices_to={'role': 'REFEREE'}
    )

    class Meta:
        db_table = 'tournaments'
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    @property
    def player_count(self):
        return self.players.count()

    @property
    def is_registration_open(self):
        return self.status == self.Status.REGISTRATION


class Match(TimestampMixin):
    """Match model representing a match within a tournament."""

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        DISPUTED = 'DISPUTED', 'Disputed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class Round(models.TextChoices):
        ROUND_128 = 'R128', 'Round of 128'
        ROUND_64 = 'R64', 'Round of 64'
        ROUND_32 = 'R32', 'Round of 32'
        ROUND_16 = 'R16', 'Round of 16'
        QUARTERFINAL = 'QF', 'Quarterfinal'
        SEMIFINAL = 'SF', 'Semifinal'
        FINAL = 'F', 'Final'

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='matches'
    )
    player1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_as_player1'
    )
    player2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches_as_player2'
    )
    referee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refereed_matches'
    )
    scheduled_time = models.DateTimeField(null=True, blank=True)
    court = models.CharField(max_length=50, blank=True)
    round = models.CharField(
        max_length=10,
        choices=Round.choices,
        default=Round.ROUND_32
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_matches'
    )

    class Meta:
        db_table = 'matches'
        ordering = ['scheduled_time']
        verbose_name_plural = 'matches'

    def __str__(self):
        p1 = self.player1.username if self.player1 else 'TBD'
        p2 = self.player2.username if self.player2 else 'TBD'
        return f"{self.tournament.name}: {p1} vs {p2} ({self.get_round_display()})"

    @property
    def is_player_assigned(self):
        return self.player1 is not None and self.player2 is not None

    def is_player_in_match(self, user):
        """Check if user is a player in this match."""
        return user in (self.player1, self.player2)
