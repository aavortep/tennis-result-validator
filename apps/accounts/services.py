from django.contrib.auth import login, logout

from core.exceptions import ValidationError, PermissionDeniedError
from .models import User


class AccountService:
    @staticmethod
    def register_user(data):
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
        login(request, user)

    @staticmethod
    def logout_user(request):
        logout(request)

    @staticmethod
    def update_profile(user, data):
        for field, value in data.items():
            if hasattr(user, field) and field not in ('password', 'role', 'is_staff', 'is_superuser'):
                setattr(user, field, value)
        user.save()
        return user

    @staticmethod
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValidationError('Current password is incorrect.')
        user.set_password(new_password)
        user.save()

    @staticmethod
    def delete_account(user, requesting_user):
        if user.id != requesting_user.id and not requesting_user.is_organizer:
            raise PermissionDeniedError('You can only delete your own account.')

        user.delete()

    @staticmethod
    def get_users_by_role(role):
        return User.objects.filter(role=role, is_active=True)

    @staticmethod
    def get_all_players():
        return User.objects.filter(role=User.Role.PLAYER, is_active=True)

    @staticmethod
    def get_all_referees():
        return User.objects.filter(role=User.Role.REFEREE, is_active=True)
