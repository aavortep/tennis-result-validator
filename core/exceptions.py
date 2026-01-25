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
    """Raised when an operation is attempted in an invalid state"""
    pass
