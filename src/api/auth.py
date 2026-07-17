from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.auth import (
    RefreshTokenRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserSchema,
)
from src.services.auth import AuthService, get_auth_service
from src.services.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register(body)
    token = await auth_service.create_email_verification_token(body.email)
    background_tasks.add_task(
        send_verification_email, body.email, token, user_info=body
    )
    return user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login(form_data.username, form_data.password)


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(
    body: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.refresh(body.refresh_token)


@router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.verify_email(token)
    return {"detail": "Email verified successfully"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.reset_password(body)
    return {"detail": "Password reset successfully"}
