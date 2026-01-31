<<<<<<< HEAD
from django.contrib.auth import login, logout

from core.exceptions import PermissionDeniedError, ValidationError

=======
"""
Business logic services for user accounts.
"""

from django.contrib.auth import login, logout

from core.exceptions import ValidationError, PermissionDeniedError
>>>>>>> main
from .models import User


class AccountService:
<<<<<<< HEAD
    @staticmethod
    def register_user(data):
        if User.objects.filter(username=data["username"]).exists():
            raise ValidationError("Username already exists.")

        if User.objects.filter(email=data["email"]).exists():
            raise ValidationError("Email already exists.")

        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            role=data.get("role", User.Role.SPECTATOR),
            phone=data.get("phone", ""),
            bio=data.get("bio", ""),
=======
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
>>>>>>> main
        )
        return user

    @staticmethod
    def login_user(request, user):
<<<<<<< HEAD
=======
        """
        Log in a user.

        Args:
            request: HTTP request
            user: User instance to log in
        """
>>>>>>> main
        login(request, user)

    @staticmethod
    def logout_user(request):
<<<<<<< HEAD
=======
        """
        Log out the current user.

        Args:
            request: HTTP request
        """
>>>>>>> main
        logout(request)

    @staticmethod
    def update_profile(user, data):
<<<<<<< HEAD
        for field, value in data.items():
            if hasattr(user, field) and field not in (
                "password",
                "role",
                "is_staff",
                "is_superuser",
            ):
=======
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
>>>>>>> main
                setattr(user, field, value)
        user.save()
        return user

    @staticmethod
    def change_password(user, old_password, new_password):
<<<<<<< HEAD
        if not user.check_password(old_password):
            raise ValidationError("Current password is incorrect.")
=======
        """
        Change user password.

        Args:
            user: User instance
            old_password: Current password
            new_password: New password
        """
        if not user.check_password(old_password):
            raise ValidationError('Current password is incorrect.')
>>>>>>> main
        user.set_password(new_password)
        user.save()

    @staticmethod
    def delete_account(user, requesting_user):
<<<<<<< HEAD
        if user.id != requesting_user.id and not requesting_user.is_organizer:
            raise PermissionDeniedError("You can only delete your own account.")
=======
        """
        Delete user account.

        Args:
            user: User to delete
            requesting_user: User making the request
        """
        if user.id != requesting_user.id and not requesting_user.is_organizer:
            raise PermissionDeniedError('You can only delete your own account.')
>>>>>>> main

        user.delete()

    @staticmethod
    def get_users_by_role(role):
<<<<<<< HEAD
=======
        """
        Get all users with a specific role.

        Args:
            role: User role string

        Returns:
            QuerySet: Users with the specified role
        """
>>>>>>> main
        return User.objects.filter(role=role, is_active=True)

    @staticmethod
    def get_all_players():
<<<<<<< HEAD
=======
        """Get all player users."""
>>>>>>> main
        return User.objects.filter(role=User.Role.PLAYER, is_active=True)

    @staticmethod
    def get_all_referees():
<<<<<<< HEAD
=======
        """Get all referee users."""
>>>>>>> main
        return User.objects.filter(role=User.Role.REFEREE, is_active=True)
