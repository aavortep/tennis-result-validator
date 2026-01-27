"""
Tests for accounts models.
"""

from django.test import TestCase

from apps.accounts.models import User


class UserModelTest(TestCase):
    """Test cases for User model."""

    def test_create_user(self):
        """Test creating a basic user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=User.Role.PLAYER
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, User.Role.PLAYER)
        self.assertTrue(user.check_password('testpass123'))

    def test_user_role_properties(self):
        """Test user role helper properties."""
        organizer = User.objects.create_user(
            username='organizer',
            email='org@example.com',
            password='pass123',
            role=User.Role.ORGANIZER
        )
        self.assertTrue(organizer.is_organizer)
        self.assertFalse(organizer.is_player)
        self.assertFalse(organizer.is_referee)
        self.assertFalse(organizer.is_spectator)

        player = User.objects.create_user(
            username='player',
            email='player@example.com',
            password='pass123',
            role=User.Role.PLAYER
        )
        self.assertTrue(player.is_player)
        self.assertFalse(player.is_organizer)

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123',
            role=User.Role.REFEREE
        )
        self.assertEqual(str(user), 'testuser (Referee)')

    def test_default_role_is_spectator(self):
        """Test that default role is spectator."""
        user = User.objects.create_user(
            username='spectator',
            email='spec@example.com',
            password='pass123'
        )
        self.assertEqual(user.role, User.Role.SPECTATOR)
