<<<<<<< HEAD
=======
"""
Role-based permissions for the Tennis Tournament application.
"""

>>>>>>> main
from rest_framework import permissions


class IsOrganizer(permissions.BasePermission):
<<<<<<< HEAD
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ORGANIZER"


class IsReferee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "REFEREE"


class IsPlayer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "PLAYER"


class IsOrganizerOrReferee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "ORGANIZER",
            "REFEREE",
=======
    """Permission class for organizer-only actions."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'ORGANIZER'
        )


class IsReferee(permissions.BasePermission):
    """Permission class for referee-only actions."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'REFEREE'
        )


class IsPlayer(permissions.BasePermission):
    """Permission class for player-only actions."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'PLAYER'
        )


class IsOrganizerOrReferee(permissions.BasePermission):
    """Permission for organizers or referees."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ('ORGANIZER', 'REFEREE')
>>>>>>> main
        )


class IsOrganizerOrReadOnly(permissions.BasePermission):
<<<<<<< HEAD
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == "ORGANIZER"


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "submitted_by"):
            return obj.submitted_by == request.user
        if hasattr(obj, "created_by"):
=======
    """
    Allow organizers full access, others read-only.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return (
            request.user.is_authenticated and
            request.user.role == 'ORGANIZER'
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners to edit.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if object has a user/owner field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'submitted_by'):
            return obj.submitted_by == request.user
        if hasattr(obj, 'created_by'):
>>>>>>> main
            return obj.created_by == request.user
        return False


class CanSubmitScore(permissions.BasePermission):
<<<<<<< HEAD
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "PLAYER",
            "REFEREE",
=======
    """Permission for users who can submit scores (players and referees)."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ('PLAYER', 'REFEREE')
>>>>>>> main
        )


class CanResolveDispute(permissions.BasePermission):
<<<<<<< HEAD
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "ORGANIZER",
            "REFEREE",
=======
    """Permission for users who can resolve disputes (organizers and referees)."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ('ORGANIZER', 'REFEREE')
>>>>>>> main
        )
