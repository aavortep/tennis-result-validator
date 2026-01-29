"""
Business logic services for tournaments.
"""

from django.db import transaction

from apps.accounts.models import User
from core.exceptions import (
    ValidationError, PermissionDeniedError, NotFoundError, InvalidStateError
)
from .models import Tournament, Match


class TournamentService:
    """Service class for tournament management operations."""

    @staticmethod
    def create_tournament(data, created_by):
        """
        Create a new tournament.

        Args:
            data: Dict containing tournament data
            created_by: User creating the tournament

        Returns:
            Tournament: Created tournament instance
        """
        if not created_by.is_organizer:
            raise PermissionDeniedError('Only organizers can create tournaments.')

        tournament = Tournament.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            start_date=data['start_date'],
            end_date=data['end_date'],
            location=data['location'],
            max_players=data.get('max_players', 32),
            created_by=created_by,
        )
        return tournament

    @staticmethod
    def update_tournament(tournament, data, user):
        """
        Update tournament details.

        Args:
            tournament: Tournament instance
            data: Dict containing update data
            user: User making the update

        Returns:
            Tournament: Updated tournament instance
        """
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can update tournaments.')

        if tournament.status in (Tournament.Status.COMPLETED, Tournament.Status.CANCELLED):
            raise InvalidStateError('Cannot update completed or cancelled tournament.')

        for field, value in data.items():
            if hasattr(tournament, field):
                setattr(tournament, field, value)
        tournament.save()
        return tournament

    @staticmethod
    def delete_tournament(tournament, user):
        """
        Delete a tournament.

        Args:
            tournament: Tournament to delete
            user: User making the request
        """
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can delete tournaments.')

        if tournament.status == Tournament.Status.IN_PROGRESS:
            raise InvalidStateError('Cannot delete tournament in progress.')

        tournament.delete()

    @staticmethod
    def add_player(tournament, player_id, user):
        """
        Add a player to a tournament.

        Args:
            tournament: Tournament instance
            player_id: ID of player to add
            user: User making the request

        Returns:
            Tournament: Updated tournament
        """
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can add players.')

        if tournament.status not in (Tournament.Status.DRAFT, Tournament.Status.REGISTRATION):
            raise InvalidStateError('Cannot add players after registration closes.')

        try:
            player = User.objects.get(id=player_id, role=User.Role.PLAYER)
        except User.DoesNotExist:
            raise NotFoundError('Player not found.')

        if tournament.players.count() >= tournament.max_players:
            raise ValidationError('Tournament is full.')

        if tournament.players.filter(id=player_id).exists():
            raise ValidationError('Player already in tournament.')

        tournament.players.add(player)
        return tournament

    @staticmethod
    def remove_player(tournament, player_id, user):
        """
        Remove a player from a tournament.

        Args:
            tournament: Tournament instance
            player_id: ID of player to remove
            user: User making the request
        """
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can remove players.')

        if tournament.status == Tournament.Status.IN_PROGRESS:
            raise InvalidStateError('Cannot remove players from tournament in progress.')

        tournament.players.remove(player_id)

    @staticmethod
    def add_referee(tournament, referee_id, user):
        """
        Add a referee to a tournament.

        Args:
            tournament: Tournament instance
            referee_id: ID of referee to add
            user: User making the request

        Returns:
            Tournament: Updated tournament
        """
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can add referees.')

        try:
            referee = User.objects.get(id=referee_id, role=User.Role.REFEREE)
        except User.DoesNotExist:
            raise NotFoundError('Referee not found.')

        if tournament.referees.filter(id=referee_id).exists():
            raise ValidationError('Referee already in tournament.')

        tournament.referees.add(referee)
        return tournament

    @staticmethod
    def open_registration(tournament, user):
        """Open tournament for registration."""
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can open registration.')

        if tournament.status != Tournament.Status.DRAFT:
            raise InvalidStateError('Can only open registration for draft tournaments.')

        tournament.status = Tournament.Status.REGISTRATION
        tournament.save()
        return tournament

    @staticmethod
    def start_tournament(tournament, user):
        """Start the tournament."""
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can start tournaments.')

        if tournament.status != Tournament.Status.REGISTRATION:
            raise InvalidStateError('Tournament must be in registration to start.')

        if tournament.players.count() < 2:
            raise ValidationError('Tournament needs at least 2 players to start.')

        tournament.status = Tournament.Status.IN_PROGRESS
        tournament.save()
        return tournament

    @staticmethod
    def complete_tournament(tournament, user):
        """Mark tournament as completed."""
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can complete tournaments.')

        tournament.status = Tournament.Status.COMPLETED
        tournament.save()
        return tournament

    @staticmethod
    def get_tournament_matches(tournament):
        """Get all matches for a tournament."""
        return tournament.matches.all()

    @staticmethod
    def get_user_tournaments(user):
        """Get tournaments for a user based on their role."""
        if user.is_organizer:
            return Tournament.objects.filter(created_by=user)
        elif user.is_player:
            return user.tournaments.all()
        elif user.is_referee:
            return user.referee_tournaments.all()
        return Tournament.objects.filter(
            status__in=[Tournament.Status.REGISTRATION, Tournament.Status.IN_PROGRESS]
        )


class MatchService:
    """Service class for match management operations."""

    @staticmethod
    def create_match(data, user):
        """
        Create a new match.

        Args:
            data: Dict containing match data
            user: User creating the match

        Returns:
            Match: Created match instance
        """
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can create matches.')

        tournament = data['tournament']
        if tournament.status not in (Tournament.Status.REGISTRATION, Tournament.Status.IN_PROGRESS):
            raise InvalidStateError('Cannot create matches for this tournament.')

        match = Match.objects.create(
            tournament=tournament,
            player1=data.get('player1'),
            player2=data.get('player2'),
            referee=data.get('referee'),
            scheduled_time=data.get('scheduled_time'),
            court=data.get('court', ''),
            round=data.get('round', Match.Round.ROUND_32),
        )
        return match

    @staticmethod
    def assign_players(match, player1_id, player2_id, user):
        """
        Assign players to a match.

        Args:
            match: Match instance
            player1_id: ID of first player
            player2_id: ID of second player
            user: User making the assignment

        Returns:
            Match: Updated match
        """
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can assign players.')

        if match.status != Match.Status.SCHEDULED:
            raise InvalidStateError('Can only assign players to scheduled matches.')

        try:
            player1 = User.objects.get(id=player1_id, role=User.Role.PLAYER)
            player2 = User.objects.get(id=player2_id, role=User.Role.PLAYER)
        except User.DoesNotExist:
            raise NotFoundError('Player not found.')

        # Verify players are in the tournament
        if not match.tournament.players.filter(id__in=[player1_id, player2_id]).count() == 2:
            raise ValidationError('Both players must be registered in the tournament.')

        match.player1 = player1
        match.player2 = player2
        match.save()
        return match

    @staticmethod
    def assign_referee(match, referee_id, user):
        """
        Assign a referee to a match.

        Args:
            match: Match instance
            referee_id: ID of referee
            user: User making the assignment

        Returns:
            Match: Updated match
        """
        if not user.is_organizer:
            raise PermissionDeniedError('Only organizers can assign referees.')

        try:
            referee = User.objects.get(id=referee_id, role=User.Role.REFEREE)
        except User.DoesNotExist:
            raise NotFoundError('Referee not found.')

        match.referee = referee
        match.save()
        return match

    @staticmethod
    def start_match(match, user):
        """Start a match."""
        if not (user.is_organizer or (user.is_referee and match.referee == user)):
            raise PermissionDeniedError('Only organizers or assigned referee can start match.')

        if match.status != Match.Status.SCHEDULED:
            raise InvalidStateError('Match must be scheduled to start.')

        if not match.is_player_assigned:
            raise ValidationError('Both players must be assigned to start match.')

        match.status = Match.Status.IN_PROGRESS
        match.save()
        return match

    @staticmethod
    def get_user_matches(user):
        """Get matches for a user based on their role."""
        if user.is_referee:
            return Match.objects.filter(referee=user)
        elif user.is_player:
            return Match.objects.filter(
                models.Q(player1=user) | models.Q(player2=user)
            )
        return Match.objects.none()

    @staticmethod
    def get_match_by_id(match_id):
        """Get a match by ID."""
        try:
            return Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            raise NotFoundError('Match not found.')


# Import for Q lookups
from django.db import models
