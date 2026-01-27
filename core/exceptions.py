"""
Custom exceptions for the Tennis Tournament application.
"""


class TennisException(Exception):
    """Base exception for tennis tournament application."""
    pass


class ValidationError(TennisException):
    """Raised when validation fails."""
    pass


class PermissionDeniedError(TennisException):
    """Raised when a user doesn't have permission for an action."""
    pass


class NotFoundError(TennisException):
    """Raised when a requested resource is not found."""
    pass


class InvalidStateError(TennisException):
    """Raised when an operation is attempted in an invalid state."""
    pass


class ScoreConflictError(TennisException):
    """Raised when there's a conflict in score submissions."""
    pass


class DisputeError(TennisException):
    """Raised when there's an issue with dispute handling."""
    pass
