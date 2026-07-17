from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.configurations import get_db_session
from src.repository.users import UserRepository
from src.services.users import UserService


def get_user_service(db: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(UserRepository(db))
