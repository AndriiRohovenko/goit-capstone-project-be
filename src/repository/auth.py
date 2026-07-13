from sqlalchemy.ext.asyncio import AsyncSession


class AuthRepository:
    """Repository for authentication-related database operations.
    Empty for now, but can be extended in the future."""

    def __init__(self, db: AsyncSession):
        self.db = db
