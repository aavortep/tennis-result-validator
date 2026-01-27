"""
Business logic services for user accounts.
"""

from django.contrib.auth import login, logout

from core.exceptions import ValidationError, PermissionDeniedError
from .models import User


class AccountService:
    """Service class for account management operations."""

    @staticmethod
    def register_user(data):
        """
        Register a new user.

        Args:
            data: Dict containing user registration data

        Returns:
            User: Created user instance
        """
        if User.objects.filter(username=data['username']).exists():
            raise ValidationError('Username already exists.')

        if User.objects.filter(email=data['email']).exists():
            raise ValidationError('Email already exists.')

        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', User.Role.SPECTATOR),
            phone=data.get('phone', ''),
            bio=data.get('bio', ''),
        )
        return user

    @staticmethod
    def login_user(request, user):
        """
        Log in a user.

        Args:
            request: HTTP request
            user: User instance to log in
        """
        login(request, user)

    @staticmethod
    def logout_user(request):
        """
        Log out the current user.

        Args:
            request: HTTP request
        """
        logout(request)

    @staticmethod
    def update_profile(user, data):
        """
        Update user profile.

        Args:
            user: User instance
            data: Dict containing update data

        Returns:
            User: Updated user instance
        """
        for field, value in data.items():
            if hasattr(user, field) and field not in ('password', 'role', 'is_staff', 'is_superuser'):
                setattr(user, field, value)
        user.save()
        return user

    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Change user password.

        Args:
            user: User instance
            old_password: Current password
            new_password: New password
        """
        if not user.check_password(old_password):
            raise ValidationError('Current password is incorrect.')
        user.set_password(new_password)
        user.save()

    @staticmethod
    def delete_account(user, requesting_user):
        """
        Delete user account.

        Args:
            user: User to delete
            requesting_user: User making the request
        """
        if user.id != requesting_user.id and not requesting_user.is_organizer:
            raise PermissionDeniedError('You can only delete your own account.')

        user.delete()

    @staticmethod
    def get_users_by_role(role):
        """
        Get all users with a specific role.

        Args:
            role: User role string

        Returns:
            QuerySet: Users with the specified role
        """
        return User.objects.filter(role=role, is_active=True)

    @staticmethod
    def get_all_players():
        """Get all player users."""
        return User.objects.filter(role=User.Role.PLAYER, is_active=True)

    @staticmethod
    def get_all_referees():
        """Get all referee users."""
        return User.objects.filter(role=User.Role.REFEREE, is_active=True)
