from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

from src.db.configurations import get_db_session
from src.conf.config import config
from src.services.users import UserService
from src.repository.users import UserRepository
from src.schemas.auth import UserSchema

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import User, UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=config.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_session)
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
        raise credentials_exception
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_db = await user_service.get_user_by_email(username)
    if user_db is None:
        raise credentials_exception
    return UserSchema.model_validate(user_db)


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only for admin users")
    return current_user
