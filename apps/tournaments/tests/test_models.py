"""
Tests for tournament models.
"""

from datetime import date, timedelta

from django.test import TestCase

from apps.accounts.models import User
from apps.tournaments.models import Match, Tournament


class TournamentModelTest(TestCase):
    """Test cases for Tournament model."""

    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizer",
            email="org@example.com",
            password="pass123",
            role=User.Role.ORGANIZER,
        )

    def test_create_tournament(self):
        """Test creating a tournament."""
        tournament = Tournament.objects.create(
            name="Test Tournament",
            description="A test tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            created_by=self.organizer,
        )

        self.assertEqual(tournament.name, "Test Tournament")
        self.assertEqual(tournament.status, Tournament.Status.DRAFT)
        self.assertEqual(tournament.created_by, self.organizer)

    def test_tournament_player_count(self):
        """Test tournament player count property."""
        tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            created_by=self.organizer,
        )

        player1 = User.objects.create_user(
            username="player1",
            email="p1@example.com",
            password="pass",
            role=User.Role.PLAYER,
        )
        player2 = User.objects.create_user(
            username="player2",
            email="p2@example.com",
            password="pass",
            role=User.Role.PLAYER,
        )

        self.assertEqual(tournament.player_count, 0)

        tournament.players.add(player1, player2)

        self.assertEqual(tournament.player_count, 2)

    def test_tournament_registration_status(self):
        """Test tournament registration status property."""
        tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            created_by=self.organizer,
        )

        self.assertFalse(tournament.is_registration_open)

        tournament.status = Tournament.Status.REGISTRATION
        tournament.save()

        self.assertTrue(tournament.is_registration_open)


class MatchModelTest(TestCase):
    """Test cases for Match model."""

    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizer",
            email="org@example.com",
            password="pass123",
            role=User.Role.ORGANIZER,
        )
        self.player1 = User.objects.create_user(
            username="player1",
            email="p1@example.com",
            password="pass123",
            role=User.Role.PLAYER,
        )
        self.player2 = User.objects.create_user(
            username="player2",
            email="p2@example.com",
            password="pass123",
            role=User.Role.PLAYER,
        )
        self.tournament = Tournament.objects.create(
            name="Test Tournament",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location="Test City",
            created_by=self.organizer,
        )

    def test_create_match(self):
        """Test creating a match."""
        match = Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2,
            round=Match.Round.QUARTERFINAL,
        )

        self.assertEqual(match.tournament, self.tournament)
        self.assertEqual(match.player1, self.player1)
        self.assertEqual(match.player2, self.player2)
        self.assertEqual(match.status, Match.Status.SCHEDULED)

    def test_match_is_player_in_match(self):
        """Test is_player_in_match method."""
        match = Match.objects.create(
            tournament=self.tournament, player1=self.player1, player2=self.player2
        )

        self.assertTrue(match.is_player_in_match(self.player1))
        self.assertTrue(match.is_player_in_match(self.player2))

        other_player = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass",
            role=User.Role.PLAYER,
        )
        self.assertFalse(match.is_player_in_match(other_player))

    def test_match_is_player_assigned(self):
        """Test is_player_assigned property."""
        match = Match.objects.create(
            tournament=self.tournament, round=Match.Round.SEMIFINAL
        )

        self.assertFalse(match.is_player_assigned)

        match.player1 = self.player1
        match.save()

        self.assertFalse(match.is_player_assigned)

        match.player2 = self.player2
        match.save()

        self.assertTrue(match.is_player_assigned)
