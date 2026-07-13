from fastapi import Request, status
from fastapi.responses import JSONResponse


# --- Custom Exceptions ---
class UserNotFoundError(Exception):
    """Raised when a user cannot be found in the database."""

    pass


class DuplicateEmailError(Exception):
    """Raised when trying to create a user with an existing email."""

    pass


class ServerError(Exception):
    """Raised for general server errors."""

    def __init__(self, message="Internal server error"):
        super().__init__(message)
        self.message = message


# --- Handlers ---
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "User not found"},
    )


async def duplicate_email_handler(request: Request, exc: DuplicateEmailError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Email already exists"},
    )


async def server_error_handler(request: Request, exc: ServerError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": exc.message},
    )
