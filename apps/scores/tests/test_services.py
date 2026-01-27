"""
Tests for score services.
"""

from datetime import date, timedelta
from django.test import TestCase

from apps.accounts.models import User
from apps.tournaments.models import Tournament, Match
from apps.scores.models import Score, Dispute, Evidence
from apps.scores.services import ScoreService, DisputeService
from core.exceptions import (
    ValidationError, PermissionDeniedError, NotFoundError, InvalidStateError,
    DisputeError
)


class ScoreServiceTest(TestCase):
    """Test cases for ScoreService."""

    def setUp(self):
        self.organizer = User.objects.create_user(
            username='organizer',
            email='org@example.com',
            password='pass123',
            role=User.Role.ORGANIZER
        )
        self.player1 = User.objects.create_user(
            username='player1',
            email='p1@example.com',
            password='pass123',
            role=User.Role.PLAYER
        )
        self.player2 = User.objects.create_user(
            username='player2',
            email='p2@example.com',
            password='pass123',
            role=User.Role.PLAYER
        )
        self.referee = User.objects.create_user(
            username='referee',
            email='ref@example.com',
            password='pass123',
            role=User.Role.REFEREE
        )
        self.tournament = Tournament.objects.create(
            name='Test Tournament',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location='Test City',
            status=Tournament.Status.IN_PROGRESS,
            created_by=self.organizer
        )
        self.tournament.players.add(self.player1, self.player2)
        self.match = Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2,
            referee=self.referee,
            status=Match.Status.IN_PROGRESS
        )

    def test_submit_score_by_player(self):
        """Test player submitting score."""
        set_scores = [
            {'player1': 6, 'player2': 4},
            {'player1': 6, 'player2': 3},
        ]

        score = ScoreService.submit_score(self.match.id, set_scores, self.player1)

        self.assertEqual(score.match, self.match)
        self.assertEqual(score.submitted_by, self.player1)
        self.assertEqual(score.winner, self.player1)
        self.assertFalse(score.is_confirmed)

    def test_submit_score_by_referee(self):
        """Test referee submitting score (auto-confirmed)."""
        set_scores = [
            {'player1': 6, 'player2': 4},
            {'player1': 6, 'player2': 3},
        ]

        score = ScoreService.submit_score(self.match.id, set_scores, self.referee)

        self.assertTrue(score.is_confirmed)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.COMPLETED)

    def test_submit_score_invalid_user(self):
        """Test score submission by non-participant fails."""
        other_player = User.objects.create_user(
            username='other', email='other@example.com',
            password='pass', role=User.Role.PLAYER
        )
        set_scores = [{'player1': 6, 'player2': 4}, {'player1': 6, 'player2': 3}]

        with self.assertRaises(PermissionDeniedError):
            ScoreService.submit_score(self.match.id, set_scores, other_player)

    def test_submit_score_invalid_scores(self):
        """Test invalid score format."""
        set_scores = [{'player1': 5, 'player2': 4}]  # Invalid - no winner

        with self.assertRaises(ValidationError):
            ScoreService.submit_score(self.match.id, set_scores, self.player1)

    def test_confirm_score(self):
        """Test confirming opponent's score."""
        set_scores = [
            {'player1': 6, 'player2': 4},
            {'player1': 6, 'player2': 3},
        ]
        score = ScoreService.submit_score(self.match.id, set_scores, self.player1)

        confirmed = ScoreService.confirm_score(score.id, self.player2)

        self.assertTrue(confirmed.is_confirmed)
        self.assertEqual(confirmed.confirmed_by, self.player2)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.COMPLETED)

    def test_confirm_own_score_fails(self):
        """Test confirming own score fails."""
        set_scores = [
            {'player1': 6, 'player2': 4},
            {'player1': 6, 'player2': 3},
        ]
        score = ScoreService.submit_score(self.match.id, set_scores, self.player1)

        with self.assertRaises(ValidationError):
            ScoreService.confirm_score(score.id, self.player1)

    def test_update_score(self):
        """Test updating score."""
        set_scores = [
            {'player1': 6, 'player2': 4},
            {'player1': 6, 'player2': 3},
        ]
        score = ScoreService.submit_score(self.match.id, set_scores, self.player1)

        new_scores = [
            {'player1': 6, 'player2': 4},
            {'player1': 7, 'player2': 5},
        ]
        updated = ScoreService.update_score(score.id, new_scores, self.player1)

        self.assertEqual(updated.set_scores, new_scores)

    def test_update_confirmed_score_fails(self):
        """Test updating confirmed score fails."""
        set_scores = [
            {'player1': 6, 'player2': 4},
            {'player1': 6, 'player2': 3},
        ]
        score = ScoreService.submit_score(self.match.id, set_scores, self.referee)

        new_scores = [{'player1': 7, 'player2': 5}, {'player1': 6, 'player2': 4}]

        with self.assertRaises(InvalidStateError):
            ScoreService.update_score(score.id, new_scores, self.referee)

    def test_delete_score(self):
        """Test deleting score."""
        set_scores = [
            {'player1': 6, 'player2': 4},
            {'player1': 6, 'player2': 3},
        ]
        score = ScoreService.submit_score(self.match.id, set_scores, self.player1)
        score_id = score.id

        ScoreService.delete_score(score_id, self.player1)

        self.assertFalse(Score.objects.filter(id=score_id).exists())


class DisputeServiceTest(TestCase):
    """Test cases for DisputeService."""

    def setUp(self):
        self.organizer = User.objects.create_user(
            username='organizer',
            email='org@example.com',
            password='pass123',
            role=User.Role.ORGANIZER
        )
        self.player1 = User.objects.create_user(
            username='player1',
            email='p1@example.com',
            password='pass123',
            role=User.Role.PLAYER
        )
        self.player2 = User.objects.create_user(
            username='player2',
            email='p2@example.com',
            password='pass123',
            role=User.Role.PLAYER
        )
        self.referee = User.objects.create_user(
            username='referee',
            email='ref@example.com',
            password='pass123',
            role=User.Role.REFEREE
        )
        self.tournament = Tournament.objects.create(
            name='Test Tournament',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location='Test City',
            status=Tournament.Status.IN_PROGRESS,
            created_by=self.organizer
        )
        self.tournament.players.add(self.player1, self.player2)
        self.match = Match.objects.create(
            tournament=self.tournament,
            player1=self.player1,
            player2=self.player2,
            referee=self.referee,
            status=Match.Status.COMPLETED
        )

    def test_create_dispute(self):
        """Test creating a dispute."""
        dispute = DisputeService.create_dispute(
            self.match.id,
            'Score was recorded incorrectly',
            self.player1
        )

        self.assertEqual(dispute.match, self.match)
        self.assertEqual(dispute.raised_by, self.player1)
        self.assertEqual(dispute.status, Dispute.Status.OPEN)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.DISPUTED)

    def test_create_duplicate_dispute_fails(self):
        """Test creating duplicate dispute fails."""
        DisputeService.create_dispute(
            self.match.id,
            'First dispute',
            self.player1
        )

        with self.assertRaises(DisputeError):
            DisputeService.create_dispute(
                self.match.id,
                'Second dispute',
                self.player2
            )

    def test_add_evidence(self):
        """Test adding evidence to dispute."""
        dispute = DisputeService.create_dispute(
            self.match.id,
            'Score dispute',
            self.player1
        )

        evidence = DisputeService.add_evidence(
            dispute.id,
            None,
            'Photo shows final score',
            self.player1
        )

        self.assertEqual(evidence.dispute, dispute)
        self.assertEqual(evidence.submitted_by, self.player1)

    def test_resolve_dispute(self):
        """Test resolving a dispute."""
        dispute = DisputeService.create_dispute(
            self.match.id,
            'Score dispute',
            self.player1
        )

        resolved = DisputeService.resolve_dispute(
            dispute.id,
            'After review, player1 wins',
            self.referee,
            winner_id=self.player1.id
        )

        self.assertEqual(resolved.status, Dispute.Status.RESOLVED)
        self.assertEqual(resolved.resolved_by, self.referee)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.COMPLETED)
        self.assertEqual(self.match.winner, self.player1)

    def test_resolve_dispute_non_referee_fails(self):
        """Test resolving dispute by non-referee fails."""
        dispute = DisputeService.create_dispute(
            self.match.id,
            'Score dispute',
            self.player1
        )

        with self.assertRaises(PermissionDeniedError):
            DisputeService.resolve_dispute(
                dispute.id,
                'My resolution',
                self.player2
            )

    def test_mark_under_review(self):
        """Test marking dispute as under review."""
        dispute = DisputeService.create_dispute(
            self.match.id,
            'Score dispute',
            self.player1
        )

        reviewed = DisputeService.mark_under_review(dispute.id, self.referee)

        self.assertEqual(reviewed.status, Dispute.Status.UNDER_REVIEW)
