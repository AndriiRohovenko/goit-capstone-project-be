from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.conf.config import config
from src.db.models import User
from src.exceptions import (
    EmailAlreadyVerifiedError,
    EmailNotVerifiedError,
    IncorrectPasswordError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotFoundError,
)
from src.schemas.auth import ResetPasswordRequest, UserCreate, UserSchema
from src.services.dependencies import get_user_service
from src.services.users import UserService
from src.services.utils import Hash

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=config.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


class AuthService:
    def __init__(self, user_service: UserService):
        self.users = user_service
        self.hash = Hash()

    async def register(self, body: UserCreate) -> User:
        return await self.users.create_user(body)

    async def create_email_verification_token(self, email: str) -> str:
        return await create_access_token(
            data={"sub": email},
            expires_delta=24 * config.JWT_EXPIRATION_SECONDS,
        )

    async def login(self, email: str, password: str) -> dict:
        user = await self.users.get_user_by_email(email)
        if not user or not self.hash.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError
        if not user.is_verified:
            raise EmailNotVerifiedError

        access_token = await create_access_token(data={"sub": user.email})
        refresh_token = await create_access_token(
            data={"sub": user.email},
            expires_delta=7 * 24 * 3600,
        )
        await self.users.update_refresh_token(user, refresh_token)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh(self, refresh_token: str | None) -> dict:
        if not refresh_token:
            raise InvalidRefreshTokenError

        user = await self.users.get_user_by_refresh_token(refresh_token)
        if not user:
            raise InvalidRefreshTokenError

        db_refresh_token = await self.users.get_refresh_token(user)
        if db_refresh_token != refresh_token:
            raise InvalidRefreshTokenError

        access_token = await create_access_token(data={"sub": user.email})
        return {
            "access_token": access_token,
            "refresh_token": db_refresh_token,
            "token_type": "bearer",
        }

    async def verify_email(self, token: str) -> None:
        user = await self.users.get_user_by_email_verification_token(token)
        if not user:
            raise UserNotFoundError
        if user.is_verified:
            raise EmailAlreadyVerifiedError
        await self.users.verify_email(user)

    async def reset_password(self, body: ResetPasswordRequest) -> None:
        user = await self.users.get_user_by_email(body.email)
        if not user:
            raise UserNotFoundError
        if not user.is_verified:
            raise EmailNotVerifiedError
        if not self.hash.verify_password(body.old_password, user.hashed_password):
            raise IncorrectPasswordError
        await self.users.reset_password(user, body.new_password)


def get_auth_service(
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(user_service)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e

    user_db = await user_service.get_user_by_email(username)
    if user_db is None:
        raise credentials_exception
    return UserSchema.model_validate(user_db)
