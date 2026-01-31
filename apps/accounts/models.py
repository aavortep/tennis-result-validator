<<<<<<< HEAD
=======
"""
User model with role-based access control.
"""

>>>>>>> main
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
<<<<<<< HEAD
    class Role(models.TextChoices):
        ORGANIZER = "ORGANIZER", "Organizer"
        REFEREE = "REFEREE", "Referee"
        PLAYER = "PLAYER", "Player"
        SPECTATOR = "SPECTATOR", "Spectator"
=======
    """Custom user model with role support."""

    class Role(models.TextChoices):
        ORGANIZER = 'ORGANIZER', 'Organizer'
        REFEREE = 'REFEREE', 'Referee'
        PLAYER = 'PLAYER', 'Player'
        SPECTATOR = 'SPECTATOR', 'Spectator'
>>>>>>> main

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SPECTATOR,
    )
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
<<<<<<< HEAD
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    class Meta:
        db_table = "users"
=======
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        db_table = 'users'
>>>>>>> main

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_organizer(self):
        return self.role == self.Role.ORGANIZER

    @property
    def is_referee(self):
        return self.role == self.Role.REFEREE

    @property
    def is_player(self):
        return self.role == self.Role.PLAYER

    @property
    def is_spectator(self):
        return self.role == self.Role.SPECTATOR
