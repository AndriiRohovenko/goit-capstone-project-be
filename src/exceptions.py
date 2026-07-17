"""Domain exceptions shared across services (not tied to the API package)."""


class UserNotFoundError(Exception):
    """Raised when a user cannot be found in the database."""


class DuplicateEmailError(Exception):
    """Raised when trying to create a user with an existing email."""


class ServerError(Exception):
    """Raised for general server errors."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message)
        self.message = message


class InvalidCredentialsError(Exception):
    """Raised when email/password authentication fails."""


class EmailNotVerifiedError(Exception):
    """Raised when an action requires a verified email."""


class InvalidRefreshTokenError(Exception):
    """Raised when a refresh token is missing or invalid."""


class EmailAlreadyVerifiedError(Exception):
    """Raised when verifying an already verified email."""


class IncorrectPasswordError(Exception):
    """Raised when the provided current password does not match."""
