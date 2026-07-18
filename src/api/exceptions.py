from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.exceptions import (
    DuplicateEmailError,
    EmailAlreadyVerifiedError,
    EmailNotVerifiedError,
    IncorrectPasswordError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    ProjectNotFoundError,
    ServerError,
    UserNotFoundError,
)

__all__ = [
    "DuplicateEmailError",
    "EmailAlreadyVerifiedError",
    "EmailNotVerifiedError",
    "IncorrectPasswordError",
    "InvalidCredentialsError",
    "InvalidRefreshTokenError",
    "ProjectNotFoundError",
    "ServerError",
    "UserNotFoundError",
    "duplicate_email_handler",
    "email_already_verified_handler",
    "email_not_verified_handler",
    "incorrect_password_handler",
    "invalid_credentials_handler",
    "invalid_refresh_token_handler",
    "project_not_found_handler",
    "server_error_handler",
    "user_not_found_handler",
]


async def user_not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "User not found"},
    )


async def duplicate_email_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": "Email already exists"},
    )


async def server_error_handler(request: Request, exc: Exception):
    message = getattr(exc, "message", "Internal server error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": message},
    )


async def invalid_credentials_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": "Incorrect email or password"},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def email_not_verified_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": "Email not verified"},
    )


async def invalid_refresh_token_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": "Invalid refresh token"},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def email_already_verified_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Email already verified"},
    )


async def incorrect_password_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Old password is incorrect"},
    )


async def project_not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Project not found"},
    )
