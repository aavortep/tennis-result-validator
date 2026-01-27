from django.db import models
from django.conf import settings

from core.mixins import TimestampMixin
from core.utils import evidence_upload_path

class Score(TimestampMixin):
    """Score model representing a match score submission"""

    match = models.ForeignKey(
        'tournaments.Match',
        on_delete=models.CASCADE,
        related_name='scores'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_scores'
    )
    set_scores = models.JSONField(
        help_text='List of set scores: [{"player1": 6, "player2": 4}, ...]'
    )
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='winning_scores'
    )
    is_confirmed = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_scores'
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'scores'
        ordering = ['-created_at']

    def __str__(self):
        return f"Score for {self.match} by {self.submitted_by.username}"


class Dispute(TimestampMixin):
    """Dispute model for contested match results"""

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        RESOLVED = 'RESOLVED', 'Resolved'

    match = models.ForeignKey(
        'tournaments.Match',
        on_delete=models.CASCADE,
        related_name='disputes'
    )
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='raised_disputes'
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_disputes'
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    final_score = models.ForeignKey(
        Score,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispute_resolutions'
    )

    class Meta:
        db_table = 'disputes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Dispute for {self.match} by {self.raised_by.username}"


class Evidence(TimestampMixin):
    """Evidence model for dispute documentation"""

    dispute = models.ForeignKey(
        Dispute,
        on_delete=models.CASCADE,
        related_name='evidence'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_evidence'
    )
    file = models.FileField(
        upload_to=evidence_upload_path,
        blank=True,
        null=True
    )
    description = models.TextField()

    class Meta:
        db_table = 'evidence'
        verbose_name_plural = 'evidence'
        ordering = ['-created_at']

    def __str__(self):
        return f"Evidence for dispute #{self.dispute.id} by {self.submitted_by.username}"
