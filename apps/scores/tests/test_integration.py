"""
Integration tests for score submission and dispute resolution workflows
"""

from datetime import date, timedelta
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import User
from apps.tournaments.models import Tournament, Match
from apps.scores.models import Score, Dispute


class ScoreSubmissionWorkflowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
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

    def test_complete_score_workflow_player_submission(self):
        """Test complete workflow: player submits, opponent confirms"""
        # Step 1: Player 1 submits score
        self.client.force_authenticate(user=self.player1)
        response = self.client.post('/api/scores/submit/', {
            'match': self.match.id,
            'set_scores': [
                {'player1': 6, 'player2': 4},
                {'player1': 6, 'player2': 3},
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        score_id = response.data['id']

        # Verify score is unconfirmed
        score = Score.objects.get(id=score_id)
        self.assertFalse(score.is_confirmed)
        self.assertEqual(score.winner, self.player1)

        # Step 2: Player 2 confirms score
        self.client.force_authenticate(user=self.player2)
        response = self.client.post(f'/api/scores/{score_id}/confirm/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify score is confirmed and match completed
        score.refresh_from_db()
        self.match.refresh_from_db()
        self.assertTrue(score.is_confirmed)
        self.assertEqual(score.confirmed_by, self.player2)
        self.assertEqual(self.match.status, Match.Status.COMPLETED)
        self.assertEqual(self.match.winner, self.player1)

    def test_referee_score_auto_confirms(self):
        self.client.force_authenticate(user=self.referee)
        response = self.client.post('/api/scores/submit/', {
            'match': self.match.id,
            'set_scores': [
                {'player1': 6, 'player2': 4},
                {'player1': 3, 'player2': 6},
                {'player1': 6, 'player2': 2},
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        score = Score.objects.get(id=response.data['id'])
        self.assertTrue(score.is_confirmed)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.COMPLETED)


class DisputeResolutionWorkflowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
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

    def test_complete_dispute_workflow(self):
        """Test complete workflow: dispute creation, evidence, resolution"""
        # Step 1: Player creates dispute
        self.client.force_authenticate(user=self.player1)
        response = self.client.post('/api/scores/disputes/create/', {
            'match': self.match.id,
            'reason': 'Score was recorded incorrectly. I won 6-4, 6-3.'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        dispute_id = response.data['id']

        # Verify match is now disputed
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.DISPUTED)

        # Step 2: Player adds evidence
        response = self.client.post('/api/scores/evidence/submit/', {
            'dispute': dispute_id,
            'description': 'Screenshot of scoreboard showing final score'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 3: Other player adds counter-evidence
        self.client.force_authenticate(user=self.player2)
        response = self.client.post('/api/scores/evidence/submit/', {
            'dispute': dispute_id,
            'description': 'My video shows different score'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 4: Referee marks as under review
        self.client.force_authenticate(user=self.referee)
        response = self.client.post(f'/api/scores/disputes/{dispute_id}/review/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dispute = Dispute.objects.get(id=dispute_id)
        self.assertEqual(dispute.status, Dispute.Status.UNDER_REVIEW)

        # Step 5: Referee resolves dispute
        response = self.client.post(f'/api/scores/disputes/{dispute_id}/resolve/', {
            'resolution_notes': 'After reviewing evidence, player1 wins.',
            'winner_id': self.player1.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify resolution
        dispute.refresh_from_db()
        self.match.refresh_from_db()
        self.assertEqual(dispute.status, Dispute.Status.RESOLVED)
        self.assertEqual(dispute.resolved_by, self.referee)
        self.assertEqual(self.match.status, Match.Status.COMPLETED)
        self.assertEqual(self.match.winner, self.player1)


class RoleBasedAccessControlTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.organizer = User.objects.create_user(
            username='organizer',
            email='org@example.com',
            password='pass123',
            role=User.Role.ORGANIZER
        )
        self.player = User.objects.create_user(
            username='player',
            email='player@example.com',
            password='pass123',
            role=User.Role.PLAYER
        )
        self.spectator = User.objects.create_user(
            username='spectator',
            email='spec@example.com',
            password='pass123',
            role=User.Role.SPECTATOR
        )

    def test_only_organizer_can_create_tournament(self):
        tournament_data = {
            'name': 'Test Tournament',
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=7)),
            'location': 'Test City',
        }

        # Organizer can create
        self.client.force_authenticate(user=self.organizer)
        response = self.client.post('/api/tournaments/', tournament_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Player cannot create
        self.client.force_authenticate(user=self.player)
        response = self.client.post('/api/tournaments/', tournament_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Spectator cannot create
        self.client.force_authenticate(user=self.spectator)
        response = self.client.post('/api/tournaments/', tournament_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_users_can_view_tournaments(self):
        Tournament.objects.create(
            name='Test Tournament',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            location='Test City',
            status=Tournament.Status.REGISTRATION,
            created_by=self.organizer
        )

        for user in [self.organizer, self.player, self.spectator]:
            self.client.force_authenticate(user=user)
            response = self.client.get('/api/tournaments/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_access_protected_endpoints(self):
        response = self.client.post('/api/scores/submit/', {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        response = self.client.post('/api/tournaments/', {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
