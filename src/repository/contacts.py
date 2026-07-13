from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import extract, and_, or_, select
from datetime import date, timedelta
from src.db.models import Contacts, User


class ContactsRepository:
    """
    Repository for managing contacts in the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        ContactsRepository: An instance of the ContactsRepository class.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int, skip: int, user: User):
        """
        Retrieve all contacts for a specific user with pagination.
        Args:
            limit (int): The maximum number of contacts to retrieve.
            skip (int): The number of contacts to skip (for pagination).
            user (User): The user whose contacts are to be retrieved.
        Returns:
            List[Contacts]: A list of contacts belonging to the user.
        """
        result = await self.db.execute(
            select(Contacts)
            .filter(Contacts.user_id == user.id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_id(self, contact_id: int, user: User):
        """
        Retrieve a contact by its ID for a specific user.
        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user whose contact is to be retrieved.
        Returns:
            Contacts | None: The contact if found, otherwise None.
        """
        result = await self.db.execute(
            select(Contacts).filter(
                Contacts.id == contact_id, Contacts.user_id == user.id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str, user: User):
        """
        Retrieve a contact by its email for a specific user.
        Args:
            email (str): The email of the contact to retrieve.
            user (User): The user whose contact is to be retrieved.
        Returns:
            Contacts | None: The contact if found, otherwise None.
        """
        result = await self.db.execute(
            select(Contacts).filter(
                Contacts.email == email, Contacts.user_id == user.id
            )
        )
        return result.scalar_one_or_none()

    async def create(self, body: Contacts, user: User, avatar: str = None):
        """
        Create a new contact for a specific user.
        Args:
            body (Contacts): The contact data to create.
            user (User): The user for whom the contact is to be created.
            avatar (str, optional): The avatar URL for the contact. Defaults to None.
        Returns:
            Contacts: The created contacts.
        """
        new_contacts = Contacts(**body.model_dump(), user_id=user.id, avatar=avatar)
        self.db.add(new_contacts)
        await self.db.commit()
        await self.db.refresh(new_contacts)
        return new_contacts

    async def update(self, existing_contact: Contacts, data: dict):
        """
        Update an existing contact with new data.
        Args:
            existing_contact (Contacts): The contact to be updated.
            data (dict): A dictionary containing the updated contact data.
            Returns:
            None: Nothing is returned.
        """
        for field, value in data.items():
            setattr(existing_contact, field, value)
        await self.db.commit()
        await self.db.refresh(existing_contact)

    async def delete(self, contact: Contacts):
        """
        Delete a contact from the database.
        Args:
            contact (Contacts): The contact to be deleted.
            Returns:
            None: Nothing is returned.
        """
        await self.db.delete(contact)
        await self.db.commit()

    async def search(
        self,
        name: str | None,
        email: str | None,
        phone: str | None,
        user: User,
    ):
        """
        Search for contacts based on name, email, and/or phone for a specific user.
        Args:
            name (str | None): The name to search for (optional).
            email (str | None): The email to search for (optional).
            phone (str | None): The phone number to search for (optional).
            user (User): The user whose contacts are to be searched.
            Returns:
            List[Contacts]: A list of contacts matching the search criteria."""
        query = select(Contacts).filter(Contacts.user_id == user.id)

        if name:
            query = query.where(Contacts.name.ilike(f"%{name}%"))
        if email:
            query = query.where(Contacts.email.ilike(f"%{email}%"))
        if phone:
            query = query.where(Contacts.phone.ilike(f"%{phone}%"))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def upcoming_birthdays(self, days: int, user: User):
        """
        Retrieve contacts with upcoming birthdays within a specified number of days for a specific user.
        Args:
            days (int): The number of days to look ahead for upcoming birthdays.
            user (User): The user whose contacts are to be checked for upcoming birthdays.
            Returns:
            List[Contacts]: A list of contacts with upcoming birthdays.
        """
        today = date.today()
        upcoming = today + timedelta(days=days)

        query = (
            select(Contacts)
            .filter(Contacts.user_id == user.id)
            .where(
                or_(
                    and_(
                        extract("month", Contacts.birthdate) == today.month,
                        extract("day", Contacts.birthdate) >= today.day,
                        extract("day", Contacts.birthdate) <= upcoming.day,
                    ),
                    and_(
                        extract("month", Contacts.birthdate) == upcoming.month,
                        extract("day", Contacts.birthdate) <= upcoming.day,
                    ),
                )
            )
        )

        result = await self.db.execute(query)
        return result.scalars().all()
