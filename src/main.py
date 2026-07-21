"""
Main application file for the FastAPI project.
Sets up the FastAPI app, middleware, routes, and exception handlers.
"""

from typing import Callable, cast

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import Response
import time

from src.api.auth import router as auth_router
from src.api.exceptions import (
    ArtifactGenerationFailedError,
    ArtifactNotFoundError,
    DuplicateEmailError,
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
    artifact_generation_failed_handler,
    artifact_not_found_handler,
    duplicate_email_handler,
    email_already_verified_handler,
    email_not_verified_handler,
    incorrect_password_handler,
    invalid_credentials_handler,
    invalid_refresh_token_handler,
    project_context_not_found_handler,
    project_not_found_handler,
    requirement_group_not_empty_handler,
    requirement_group_not_found_handler,
    requirement_not_found_handler,
    server_error_handler,
    unsupported_generation_type_handler,
    user_not_found_handler,
)
from src.api.users import router as users_router
from src.api.utils import router as utils_router
from src.api.projects import router as projects_router
from src.api.requirements import router as requirements_router
from src.api.requirement_groups import router as requirement_groups_router
from src.api.artifacts import router as artifacts_router
from src.conf.limiter import limiter
app = FastAPI()
app.state.limiter = limiter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Hello from FastAPI! Read the docs at /docs"}


app.add_exception_handler(UserNotFoundError, user_not_found_handler)
app.add_exception_handler(DuplicateEmailError, duplicate_email_handler)
app.add_exception_handler(ServerError, server_error_handler)
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
app.add_exception_handler(EmailNotVerifiedError, email_not_verified_handler)
app.add_exception_handler(InvalidRefreshTokenError, invalid_refresh_token_handler)
app.add_exception_handler(EmailAlreadyVerifiedError, email_already_verified_handler)
app.add_exception_handler(IncorrectPasswordError, incorrect_password_handler)
app.add_exception_handler(ProjectNotFoundError, project_not_found_handler)
app.add_exception_handler(ProjectContextNotFoundError, project_context_not_found_handler)
app.add_exception_handler(RequirementNotFoundError, requirement_not_found_handler)
app.add_exception_handler(
    RequirementGroupNotFoundError, requirement_group_not_found_handler
)
app.add_exception_handler(
    RequirementGroupNotEmptyError, requirement_group_not_empty_handler
)
app.add_exception_handler(ArtifactNotFoundError, artifact_not_found_handler)
app.add_exception_handler(
    ArtifactGenerationFailedError, artifact_generation_failed_handler
)
app.add_exception_handler(
    UnsupportedGenerationTypeError, unsupported_generation_type_handler
)

RateLimitExceptionHandler = Callable[[Request, Exception], Response]
app.add_exception_handler(
    RateLimitExceeded,
    cast(RateLimitExceptionHandler, _rate_limit_exceeded_handler),
)

app.include_router(users_router, prefix="/api")
app.include_router(utils_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(requirement_groups_router, prefix="/api")
app.include_router(requirements_router, prefix="/api")
app.include_router(artifacts_router, prefix="/api")
