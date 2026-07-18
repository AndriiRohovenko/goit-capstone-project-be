from jose import jwt

from src.conf.config import config
from src.db.models import User
from src.exceptions import DuplicateEmailError, ServerError, UserNotFoundError
from src.repository.users import UserRepository
from src.schemas.auth import UserCreate
from src.services.utils import Hash

SECRET_KEY = config.JWT_SECRET
ALGORITHM = config.JWT_ALGORITHM


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
        self.hash = Hash()

    async def get_refresh_token(self, user: User):
        user = await self.repo.get_by_id(user.id)
        if not user:
            raise UserNotFoundError
        return user.refresh_token

    async def update_refresh_token(self, user: User, refresh_token: str):
        user = await self.repo.get_by_id(user.id)
        if not user:
            raise UserNotFoundError
        try:
            return await self.repo.update(user, {"refresh_token": refresh_token})
        except Exception as e:
            raise ServerError(str(e)) from e

    async def get_user_by_refresh_token(self, refresh_token: str):
        return await self.repo.get_user_by_refresh_token(refresh_token)

    async def get_user_by_email_verification_token(self, token: str):
        email = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
        return await self.repo.get_by_email(email)

    async def create_user(self, data: UserCreate):
        if await self.repo.get_by_email(data.email):
            raise DuplicateEmailError
        try:
            hashed_password = self.hash.get_password_hash(data.password)
            return await self.repo.create(
                data,
                hashed_password=hashed_password,
            )
        except DuplicateEmailError:
            raise
        except Exception as e:
            raise ServerError(str(e)) from e

    async def update_user(self, user: User, data):
        existing = await self.repo.get_by_id(user.id)
        if not existing:
            raise UserNotFoundError
        if await self.repo.get_by_email(data.email) and existing.email != data.email:
            raise DuplicateEmailError
        try:
            return await self.repo.update(existing, data.dict())
        except Exception as e:
            raise ServerError(str(e)) from e

    async def delete_user(self, user: User):
        existing = await self.repo.get_by_id(user.id)
        if not existing:
            raise UserNotFoundError
        try:
            await self.repo.delete(existing)
        except Exception as e:
            raise ServerError(str(e)) from e

    async def get_user_by_email(self, email: str):
        try:
            return await self.repo.get_by_email(email)
        except Exception as e:
            raise ServerError(str(e)) from e

    async def verify_email(self, user: User):
        existing = await self.repo.get_by_id(user.id)
        if not existing:
            raise UserNotFoundError
        try:
            return await self.repo.confirm_email(existing)
        except Exception as e:
            raise ServerError(str(e)) from e

    async def update_avatar_url(self, email: str, url: str):
        return await self.repo.update_avatar_url(email, url)

    async def reset_password(self, user: User, new_password: str):
        try:
            hashed_new_password = self.hash.get_password_hash(new_password)
            return await self.repo.update(
                user, {"hashed_password": hashed_new_password}
            )
        except Exception as e:
            raise ServerError(str(e)) from e
