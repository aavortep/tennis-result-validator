from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.tournaments.models import Match
from core.exceptions import (
    DisputeError,
    InvalidStateError,
    NotFoundError,
    PermissionDeniedError,
    ScoreConflictError,
    ValidationError,
)
from core.utils import determine_match_winner, validate_set_scores

from .models import Dispute, Evidence, Score


class ScoreService:
    @staticmethod
    def submit_score(match_id, set_scores, user):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            raise NotFoundError("Match not found.")

        if user.is_player:
            if not match.is_player_in_match(user):
                raise PermissionDeniedError("You are not a player in this match.")
        elif user.is_referee:
            if match.referee != user:
                raise PermissionDeniedError("You are not the referee for this match.")
        else:
            raise PermissionDeniedError("Only players and referees can submit scores.")

        if match.status not in (Match.Status.IN_PROGRESS, Match.Status.COMPLETED):
            raise InvalidStateError(
                "Match must be in progress or completed to submit score."
            )

        is_valid, error = validate_set_scores(set_scores)
        if not is_valid:
            raise ValidationError(error)

        existing_score = Score.objects.filter(match=match, submitted_by=user).first()
        if existing_score:
            raise ValidationError("You have already submitted a score for this match.")

        winner_key = determine_match_winner(set_scores)
        winner = None
        if winner_key:
            winner = match.player1 if winner_key == "player1" else match.player2

        score = Score.objects.create(
            match=match,
            submitted_by=user,
            set_scores=set_scores,
            winner=winner,
            is_confirmed=user.is_referee,
        )

        if user.is_referee:
            ScoreService._finalize_match(match, score)

        return score

    @staticmethod
    def update_score(score_id, set_scores, user):
        try:
            score = Score.objects.get(id=score_id)
        except Score.DoesNotExist:
            raise NotFoundError("Score not found.")

        if score.submitted_by != user:
            raise PermissionDeniedError(
                "You can only update your own score submission."
            )

        if score.is_confirmed:
            raise InvalidStateError("Cannot update confirmed score.")

        is_valid, error = validate_set_scores(set_scores)
        if not is_valid:
            raise ValidationError(error)

        winner_key = determine_match_winner(set_scores)
        winner = None
        if winner_key:
            match = score.match
            winner = match.player1 if winner_key == "player1" else match.player2

        score.set_scores = set_scores
        score.winner = winner
        score.save()

        return score

    @staticmethod
    def delete_score(score_id, user):
        try:
            score = Score.objects.get(id=score_id)
        except Score.DoesNotExist:
            raise NotFoundError("Score not found.")

        if score.submitted_by != user and not user.is_organizer:
            raise PermissionDeniedError(
                "You can only delete your own score submission."
            )

        if score.is_confirmed and not user.is_organizer:
            raise InvalidStateError("Cannot delete confirmed score.")

        score.delete()

    @staticmethod
    def confirm_score(score_id, user):
        try:
            score = Score.objects.get(id=score_id)
        except Score.DoesNotExist:
            raise NotFoundError("Score not found.")

        match = score.match

        if user.is_player:
            if not match.is_player_in_match(user):
                raise PermissionDeniedError("You are not a player in this match.")
            if score.submitted_by == user:
                raise ValidationError("You cannot confirm your own score.")

        elif user.is_referee:
            if match.referee != user:
                raise PermissionDeniedError("You are not the referee for this match.")
        else:
            raise PermissionDeniedError("Only players and referees can confirm scores.")

        if score.is_confirmed:
            raise ValidationError("Score is already confirmed.")

        score.is_confirmed = True
        score.confirmed_by = user
        score.confirmed_at = timezone.now()
        score.save()

        ScoreService._finalize_match(match, score)

        return score

    @staticmethod
    def _finalize_match(match, score):
        match.status = Match.Status.COMPLETED
        match.winner = score.winner
        match.save()

    @staticmethod
    def get_match_scores(match_id):
        return Score.objects.filter(match_id=match_id)


class DisputeService:
    @staticmethod
    def create_dispute(match_id, reason, user):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            raise NotFoundError("Match not found.")

        if not user.is_player or not match.is_player_in_match(user):
            raise PermissionDeniedError(
                "Only players in this match can raise disputes."
            )

        existing_dispute = Dispute.objects.filter(
            match=match, status__in=[Dispute.Status.OPEN, Dispute.Status.UNDER_REVIEW]
        ).exists()
        if existing_dispute:
            raise DisputeError("There is already an open dispute for this match.")

        dispute = Dispute.objects.create(match=match, raised_by=user, reason=reason)

        match.status = Match.Status.DISPUTED
        match.save()

        return dispute

    @staticmethod
    def add_evidence(dispute_id, file, description, user):
        try:
            dispute = Dispute.objects.get(id=dispute_id)
        except Dispute.DoesNotExist:
            raise NotFoundError("Dispute not found.")

        if dispute.status == Dispute.Status.RESOLVED:
            raise InvalidStateError("Cannot add evidence to resolved dispute.")

        match = dispute.match
        if user.is_player:
            if not match.is_player_in_match(user):
                raise PermissionDeniedError("You are not a player in this match.")
        elif not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError("Only involved parties can submit evidence.")

        evidence = Evidence.objects.create(
            dispute=dispute, submitted_by=user, file=file, description=description
        )

        return evidence

    @staticmethod
    @transaction.atomic
    def resolve_dispute(
        dispute_id, resolution_notes, user, final_score_id=None, winner_id=None
    ):
        try:
            dispute = Dispute.objects.get(id=dispute_id)
        except Dispute.DoesNotExist:
            raise NotFoundError("Dispute not found.")

        if not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError(
                "Only referees and organizers can resolve disputes."
            )

        if user.is_referee and dispute.match.referee != user:
            raise PermissionDeniedError("You are not the referee for this match.")

        if dispute.status == Dispute.Status.RESOLVED:
            raise InvalidStateError("Dispute is already resolved.")

        match = dispute.match

        final_score = None
        if final_score_id:
            try:
                final_score = Score.objects.get(id=final_score_id, match=match)
            except Score.DoesNotExist:
                raise NotFoundError("Final score not found.")

        winner = None
        if winner_id:
            try:
                winner = User.objects.get(id=winner_id)
                if not match.is_player_in_match(winner):
                    raise ValidationError("Winner must be a player in the match.")
            except User.DoesNotExist:
                raise NotFoundError("Winner not found.")
        elif final_score:
            winner = final_score.winner

        dispute.status = Dispute.Status.RESOLVED
        dispute.resolved_by = user
        dispute.resolution_notes = resolution_notes
        dispute.resolved_at = timezone.now()
        dispute.final_score = final_score
        dispute.save()

        match.status = Match.Status.COMPLETED
        match.winner = winner
        match.save()

        return dispute

    @staticmethod
    def get_dispute_evidence(dispute_id):
        return Evidence.objects.filter(dispute_id=dispute_id)

    @staticmethod
    def get_open_disputes():
        return Dispute.objects.filter(
            status__in=[Dispute.Status.OPEN, Dispute.Status.UNDER_REVIEW]
        )

    @staticmethod
    def mark_under_review(dispute_id, user):
        try:
            dispute = Dispute.objects.get(id=dispute_id)
        except Dispute.DoesNotExist:
            raise NotFoundError("Dispute not found.")

        if not (user.is_referee or user.is_organizer):
            raise PermissionDeniedError(
                "Only referees and organizers can review disputes."
            )

        dispute.status = Dispute.Status.UNDER_REVIEW
        dispute.save()

        return dispute
