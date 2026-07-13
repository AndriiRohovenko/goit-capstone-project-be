from src.repository.contacts import ContactsRepository
from src.db.models import Contacts
from src.api.exceptions import UserNotFoundError, DuplicateEmailError, ServerError

from libgravatar import Gravatar
from src.db.models import User


class ContactService:

    def __init__(self, repo: ContactsRepository):
        self.repo = repo

    async def get_contacts(self, user: User, limit: int, skip: int):
        try:
            return await self.repo.get_all(user=user, limit=limit, skip=skip)
        except Exception as e:
            raise ServerError(str(e))

    async def get_contact(self, contact_id: int, user: User):
        try:
            contact = await self.repo.get_by_id(contact_id=contact_id, user=user)
            if contact is None:
                raise UserNotFoundError
            return contact
        except UserNotFoundError:
            raise
        except Exception as e:
            raise ServerError(str(e))

    async def create_contact(self, data: Contacts, user: User):
        if await self.repo.get_by_email(email=data.email, user=user):
            raise DuplicateEmailError
        try:
            g = Gravatar(data.email)
            avatar = g.get_image()

            return await self.repo.create(data, user=user, avatar=avatar)
        except Exception as e:
            raise ServerError(str(e))

    async def update_contact(self, contact_id: int, data: Contacts, user: User):
        existing = await self.repo.get_by_id(contact_id=contact_id, user=user)
        if not existing:
            raise UserNotFoundError
        if (
            await self.repo.get_by_email(email=data.email, user=user)
            and existing.email != data.email
        ):
            raise DuplicateEmailError
        try:
            return await self.repo.update(existing, data.model_dump(exclude_unset=True))
        except Exception as e:
            raise ServerError(str(e))

    async def delete_contact(self, contact_id: int, user: User):
        existing = await self.repo.get_by_id(contact_id=contact_id, user=user)
        if not existing:
            raise UserNotFoundError
        try:
            return await self.repo.delete(existing)
        except Exception as e:
            raise ServerError(str(e))

    async def search_contacts(
        self,
        name: str | None,
        email: str | None,
        phone: str | None,
        user: User,
    ):
        try:
            return await self.repo.search(name, email, phone, user=user)
        except Exception as e:
            raise ServerError(str(e))

    async def upcoming_birthdays(self, days: int, user: User):
        try:
            return await self.repo.upcoming_birthdays(days, user=user)
        except Exception as e:
            raise ServerError(str(e))
