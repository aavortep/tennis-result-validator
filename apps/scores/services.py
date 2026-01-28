"""
Business logic services for scores and disputes
"""

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.tournaments.models import Match
from core.exceptions import (
    ValidationError, PermissionDeniedError, NotFoundError, InvalidStateError, DisputeError
)
from core.utils import validate_set_scores, determine_match_winner
from .models import Score, Dispute, Evidence


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
    
    @staticmethod
    def create_dispute(match_id, reason, user):
        """
        Create a dispute for a match.

        Args:
            match_id: ID of the match
            reason: Reason for dispute
            user: User raising the dispute

        Returns:
            Dispute: Created dispute instance
        """
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            raise NotFoundError('Match not found.')

        # Only players in the match can dispute
        if not user.is_player or not match.is_player_in_match(user):
            raise PermissionDeniedError('Only players in this match can raise disputes.')

        # Check for existing open dispute
        existing_dispute = Dispute.objects.filter(
            match=match,
            status__in=[Dispute.Status.OPEN, Dispute.Status.UNDER_REVIEW]
        ).exists()
        if existing_dispute:
            raise DisputeError('There is already an open dispute for this match.')

        dispute = Dispute.objects.create(
            match=match,
            raised_by=user,
            reason=reason
        )

        # Update match status
        match.status = Match.Status.DISPUTED
        match.save()

        return dispute
    
    @staticmethod
    @transaction.atomic
    def resolve_dispute(dispute_id, resolution_notes, user, final_score_id=None, winner_id=None):
        """
        Args:
            dispute_id: ID of the dispute
            resolution_notes: Resolution explanation
            user: User resolving the dispute
            final_score_id: ID of accepted score (optional)
            winner_id: ID of declared winner (optional)

        Returns:
            Dispute: Resolved dispute instance
        """
        try:
            dispute = Dispute.objects.get(id=dispute_id)
        except Dispute.DoesNotExist:
            raise NotFoundError('Dispute not found.')

        # Only referee or organizer can resolve
        if not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError('Only referees and organizers can resolve disputes.')

        if user.is_referee and dispute.match.referee != user:
            raise PermissionDeniedError('You are not the referee for this match.')

        if dispute.status == Dispute.Status.RESOLVED:
            raise InvalidStateError('Dispute is already resolved.')

        match = dispute.match

        # Handle final score
        final_score = None
        if final_score_id:
            try:
                final_score = Score.objects.get(id=final_score_id, match=match)
            except Score.DoesNotExist:
                raise NotFoundError('Final score not found.')

        # Handle declared winner
        winner = None
        if winner_id:
            try:
                winner = User.objects.get(id=winner_id)
                if not match.is_player_in_match(winner):
                    raise ValidationError('Winner must be a player in the match.')
            except User.DoesNotExist:
                raise NotFoundError('Winner not found.')
        elif final_score:
            winner = final_score.winner

        # Update dispute
        dispute.status = Dispute.Status.RESOLVED
        dispute.resolved_by = user
        dispute.resolution_notes = resolution_notes
        dispute.resolved_at = timezone.now()
        dispute.final_score = final_score
        dispute.save()

        # Update match
        match.status = Match.Status.COMPLETED
        match.winner = winner
        match.save()

        return dispute
    
    @staticmethod
    def add_evidence(dispute_id, file, description, user):
        """
        Add evidence to a dispute.

        Args:
            dispute_id: ID of the dispute
            file: Evidence file (optional)
            description: Evidence description
            user: User submitting evidence

        Returns:
            Evidence: Created evidence instance
        """
        try:
            dispute = Dispute.objects.get(id=dispute_id)
        except Dispute.DoesNotExist:
            raise NotFoundError('Dispute not found.')

        # Check dispute is still open
        if dispute.status == Dispute.Status.RESOLVED:
            raise InvalidStateError('Cannot add evidence to resolved dispute.')

        # Players in match or referee/organizer can submit evidence
        match = dispute.match
        if user.is_player:
            if not match.is_player_in_match(user):
                raise PermissionDeniedError('You are not a player in this match.')
        elif not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError('Only involved parties can submit evidence.')

        evidence = Evidence.objects.create(
            dispute=dispute,
            submitted_by=user,
            file=file,
            description=description
        )

        return evidence
    
    @staticmethod
    def get_dispute_evidence(dispute_id):
        """Get all evidence for a dispute"""
        return Evidence.objects.filter(dispute_id=dispute_id)
    
    @staticmethod
    def mark_under_review(dispute_id, user):
        """Mark a dispute as under review"""
        try:
            dispute = Dispute.objects.get(id=dispute_id)
        except Dispute.DoesNotExist:
            raise NotFoundError('Dispute not found.')

        if not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError('Only referees and organizers can review disputes.')

        dispute.status = Dispute.Status.UNDER_REVIEW
        dispute.save()

        return dispute
