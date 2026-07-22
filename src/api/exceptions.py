from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.exceptions import (
    ArtifactGenerationFailedError,
    ArtifactNotFoundError,
    CoverageReportNotFoundError,
    DuplicateEmailError,
    DuplicateRequirementGroupNameError,
    EmailAlreadyVerifiedError,
    EmailNotVerifiedError,
    IncorrectPasswordError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    ProjectContextNotFoundError,
    ProjectNotFoundError,
    RequirementGroupNotEmptyError,
    RequirementGroupNotFoundError,
    RequirementNotFoundError,
    ServerError,
    UnsupportedGenerationTypeError,
    UserNotFoundError,
)

__all__ = [
    "ArtifactGenerationFailedError",
    "ArtifactNotFoundError",
    "CoverageReportNotFoundError",
    "DuplicateEmailError",
    "DuplicateRequirementGroupNameError",
    "EmailAlreadyVerifiedError",
    "EmailNotVerifiedError",
    "IncorrectPasswordError",
    "InvalidCredentialsError",
    "InvalidRefreshTokenError",
    "ProjectContextNotFoundError",
    "ProjectNotFoundError",
    "RequirementGroupNotEmptyError",
    "RequirementGroupNotFoundError",
    "RequirementNotFoundError",
    "ServerError",
    "UnsupportedGenerationTypeError",
    "UserNotFoundError",
    "artifact_generation_failed_handler",
    "artifact_not_found_handler",
    "coverage_report_not_found_handler",
    "duplicate_email_handler",
    "duplicate_requirement_group_name_handler",
    "email_already_verified_handler",
    "email_not_verified_handler",
    "incorrect_password_handler",
    "invalid_credentials_handler",
    "invalid_refresh_token_handler",
    "project_context_not_found_handler",
    "project_not_found_handler",
    "requirement_group_not_empty_handler",
    "requirement_group_not_found_handler",
    "requirement_not_found_handler",
    "server_error_handler",
    "unsupported_generation_type_handler",
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


async def project_context_not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Project context not found"},
    )


async def requirement_not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Requirement not found"},
    )


async def requirement_group_not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Requirement group not found"},
    )


async def requirement_group_not_empty_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": "Requirement group still has requirements"},
    )


async def duplicate_requirement_group_name_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": "Requirement group name already exists"},
    )


async def artifact_not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Artifact not found"},
    )


async def artifact_generation_failed_handler(request: Request, exc: Exception):
    message = getattr(exc, "message", "AI generation failed")
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"message": message},
    )


async def unsupported_generation_type_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Unsupported generation type"},
    )


async def coverage_report_not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Coverage report not found"},
    )
