from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.schemas.auth import UserCreate


class UserRepository:
    """Repository for managing users in the database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_refresh_token(self, refresh_token: str):
        result = await self.db.execute(
            select(User).filter(User.refresh_token == refresh_token)
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int, skip: int):
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_id(self, user_id: UUID):
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def create(
        self,
        body: UserCreate,
        hashed_password: str,
        avatar: str | None = None,
    ):
        user_data = body.model_dump(exclude={"password"})
        new_user = User(
            **user_data,
            hashed_password=hashed_password,
            avatar=avatar,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update(self, existing_user: User, data: dict):
        for field, value in data.items():
            setattr(existing_user, field, value)
        await self.db.commit()
        await self.db.refresh(existing_user)
        return existing_user

    async def delete(self, user: User):
        try:
            await self.db.delete(user)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False

    async def confirm_email(self, user: User):
        user.is_verified = True
        await self.db.commit()
        await self.db.refresh(user)

    async def update_avatar_url(self, email: str, url: str):
        user = await self.get_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
