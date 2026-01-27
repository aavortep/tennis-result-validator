"""
Business logic services for scores and disputes
"""

from django.utils import timezone

from apps.tournaments.models import Match
from core.exceptions import (
    ValidationError, PermissionDeniedError, NotFoundError, InvalidStateError
)
from core.utils import validate_set_scores, determine_match_winner
from .models import Score, Dispute


class ScoreService:
    @staticmethod
    def submit_score(match_id, set_scores, user):
        """
        Args:
            match_id: ID of the match
            set_scores: List of set scores
            user: User submitting the score

        Returns:
            Score: Created score instance
        """
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            raise NotFoundError('Match not found.')

        # Validate user can submit score
        if user.is_player:
            if not match.is_player_in_match(user):
                raise PermissionDeniedError('You are not a player in this match.')
        elif user.is_referee:
            if match.referee != user:
                raise PermissionDeniedError('You are not the referee for this match.')
        else:
            raise PermissionDeniedError('Only players and referees can submit scores.')

        # Validate match state
        if match.status not in (Match.Status.IN_PROGRESS, Match.Status.COMPLETED):
            raise InvalidStateError('Match must be in progress or completed to submit score.')

        # Validate set scores
        is_valid, error = validate_set_scores(set_scores)
        if not is_valid:
            raise ValidationError(error)

        # Check for existing score from this user
        existing_score = Score.objects.filter(match=match, submitted_by=user).first()
        if existing_score:
            raise ValidationError('You have already submitted a score for this match.')

        # Determine winner
        winner_key = determine_match_winner(set_scores)
        winner = None
        if winner_key:
            winner = match.player1 if winner_key == 'player1' else match.player2

        score = Score.objects.create(
            match=match,
            submitted_by=user,
            set_scores=set_scores,
            winner=winner,
            is_confirmed=user.is_referee  # Auto-confirm referee scores
        )

        # If referee submitted, update match
        if user.is_referee:
            ScoreService._finalize_match(match, score)

        return score
    
    
    @staticmethod
    def confirm_score(score_id, user):
        """
        Confirm an opponent's score submission.
        Args:
            score_id: ID of the score
            user: User confirming the score

        Returns:
            Score: Confirmed score instance
        """
        try:
            score = Score.objects.get(id=score_id)
        except Score.DoesNotExist:
            raise NotFoundError('Score not found.')

        match = score.match

        # Player can confirm opponent's score
        if user.is_player:
            if not match.is_player_in_match(user):
                raise PermissionDeniedError('You are not a player in this match.')
            if score.submitted_by == user:
                raise ValidationError('You cannot confirm your own score.')

        # Referee can confirm any score for their match
        elif user.is_referee:
            if match.referee != user:
                raise PermissionDeniedError('You are not the referee for this match.')
        else:
            raise PermissionDeniedError('Only players and referees can confirm scores.')

        if score.is_confirmed:
            raise ValidationError('Score is already confirmed.')

        score.is_confirmed = True
        score.confirmed_by = user
        score.confirmed_at = timezone.now()
        score.save()

        # Finalize match
        ScoreService._finalize_match(match, score)

        return score
    
    @staticmethod
    def update_score(score_id, set_scores, user):
        """
        Args:
            score_id: ID of the score
            set_scores: Updated set scores
            user: User updating the score

        Returns:
            Score: Updated score instance
        """
        try:
            score = Score.objects.get(id=score_id)
        except Score.DoesNotExist:
            raise NotFoundError('Score not found.')

        # Only submitter can update
        if score.submitted_by != user:
            raise PermissionDeniedError('You can only update your own score submission.')

        # Cannot update confirmed scores
        if score.is_confirmed:
            raise InvalidStateError('Cannot update confirmed score.')

        # Validate set scores
        is_valid, error = validate_set_scores(set_scores)
        if not is_valid:
            raise ValidationError(error)

        # Update winner
        winner_key = determine_match_winner(set_scores)
        winner = None
        if winner_key:
            match = score.match
            winner = match.player1 if winner_key == 'player1' else match.player2

        score.set_scores = set_scores
        score.winner = winner
        score.save()

        return score
    
    @staticmethod
    def delete_score(score_id, user):
        """
        Args:
            score_id: ID of the score
            user: User deleting the score
        """
        try:
            score = Score.objects.get(id=score_id)
        except Score.DoesNotExist:
            raise NotFoundError('Score not found.')

        # Only submitter or organizer can delete
        if score.submitted_by != user and not user.is_organizer:
            raise PermissionDeniedError('You can only delete your own score submission.')

        # Cannot delete confirmed scores
        if score.is_confirmed and not user.is_organizer:
            raise InvalidStateError('Cannot delete confirmed score.')

        score.delete()
    
    @staticmethod
    def get_match_scores(match_id):
        """Get all scores for a match."""
        return Score.objects.filter(match_id=match_id)

    @staticmethod
    def _finalize_match(match, score):
        match.status = Match.Status.COMPLETED
        match.winner = score.winner
        match.save()


class DisputeService:
    """Service class for dispute management operations"""

    @staticmethod
    def get_open_disputes():
        return Dispute.objects.filter(
            status__in=[Dispute.Status.OPEN, Dispute.Status.UNDER_REVIEW]
        )
