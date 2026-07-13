from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.models import User
from src.schemas.auth import UserCreate
from src.api.utils import hash_password


class UserRepository:
    """
    Repository for managing users in the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        UserRepository: An instance of the UserRepository class.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_refresh_token(self, refresh_token: str):
        """Retrieve a user by their refresh token.
        Args:
            refresh_token (str): The refresh token to search for.

        Returns:
            User | None: The user if found, otherwise None.
        """
        result = await self.db.execute(
            select(User).filter(User.refresh_token == refresh_token)
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int, skip: int):
        """Retrieve all users with pagination.
        Args:
            limit (int): The maximum number of users to return.
            skip (int): The number of users to skip.

        Returns:
            List[User]: A list of users.
        """
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_id(self, user_id: int):
        """
        Retrieve a user by their ID.
        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str):
        """
        Retrieve a user by their email.
        Args:
            email (str): The email of the user to retrieve.

        Returns:
            User | None: The user if found, otherwise None.
        """
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, body: UserCreate, avatar: str = None):
        """Create a new user.
        Args:
            body (UserCreate): The user data.
            avatar (str, optional): The URL of the user's avatar. Defaults to None.

        Returns:
            User | None: The created user if successful, otherwise None.
        """

        hashed_password = hash_password(body.password)
        user_data = body.model_dump(exclude={"password"})

        new_user = User(**user_data, hashed_password=hashed_password, avatar=avatar)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update(self, existing_user: User, data: dict):
        """Update an existing user.
        Args:
            existing_user (User): The user to update.
            data (dict): The data to update the user with.

        Returns:
            User | None: The updated user if successful, otherwise None.
        """
        for field, value in data.items():
            setattr(existing_user, field, value)
        await self.db.commit()
        await self.db.refresh(existing_user)
        return existing_user

    async def delete(self, user: User):
        """Delete a user.
        Args:
            user (User): The user to delete.
            Returns:
             Note: Nothing returned, user is deleted from the database.
        """
        try:
            await self.db.delete(user)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            return False

    async def confirm_email(self, user: User):
        """Confirm a user's email.
        Args:
            user (User): The user to confirm.
            Returns:
             Note: Nothing returned, user's email is confirmed in the database.
        """
        user.is_verified = True
        await self.db.commit()
        await self.db.refresh(user)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update a user's avatar URL.
        Args:
            email (str): The email of the user to update.
            url (str): The new avatar URL.
            Returns:
             Note: Nothing returned, user's avatar URL is updated in the database.
        """
        user = await self.get_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
