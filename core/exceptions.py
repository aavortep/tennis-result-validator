class TennisException(Exception):
    """Base exception"""
    pass


class ValidationError(TennisException):
    pass


class PermissionDeniedError(TennisException):
    pass


class NotFoundError(TennisException):
    pass


class InvalidStateError(TennisException):
    """Raised when an operation is attempted in an invalid state."""
    pass


class ScoreConflictError(TennisException):
    """Raised when there's a conflict in score submissions."""
    pass


class DisputeError(TennisException):
    pass
