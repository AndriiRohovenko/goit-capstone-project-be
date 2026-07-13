from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from src.db.configurations import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.contacts import ContactSchema
from src.services.auth import get_current_user
from src.services.contacts import ContactService
from src.repository.contacts import ContactsRepository


router = APIRouter(prefix="/contacts", tags=["contacts"])


async def contact_service(db: AsyncSession = Depends(get_db_session)):
    """
    Dependency to get ContactService instance.
    Args:
        db (AsyncSession): Database session dependency.
    Returns: ContactService instance.
    """
    repo = ContactsRepository(db)
    return ContactService(repo)


@router.get(
    "/",
    response_model=list[ContactSchema],
    status_code=status.HTTP_200_OK,
)
async def get_contacts(
    skip: int = 0,
    limit: int = 25,
    service: ContactService = Depends(contact_service),
    current_user=Depends(get_current_user),
):
    """
    Retrieve a list of contacts for the current user with pagination.
    Args:
        skip (int): Number of records to skip for pagination. Default is 0.
        limit (int): Maximum number of records to return. Default is 25.
        service (ContactService): Contact service dependency.
        current_user: The currently authenticated user.
    Returns: A list of contacts belonging to the current user.
    """
    return await service.get_contacts(user=current_user, skip=skip, limit=limit)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    contact: ContactSchema,
    service: ContactService = Depends(contact_service),
    current_user=Depends(get_current_user),
):
    """
    Create a new contact for the current user.
    Args:
        contact (ContactSchema): The contact data to create.
        service (ContactService): Contact service dependency.
        current_user: The currently authenticated user.
    Returns: The created contact.
    """
    return await service.create_contact(contact, user=current_user)


@router.get(
    "/{contact_id}",
    response_model=ContactSchema,
    status_code=status.HTTP_200_OK,
)
async def get_contact(
    contact_id: int,
    service: ContactService = Depends(contact_service),
    current_user=Depends(get_current_user),
):
    """
    Retrieve a specific contact for the current user.
    Args:
        contact_id (int): The ID of the contact to retrieve.
        service (ContactService): Contact service dependency.
        current_user: The currently authenticated user.
    Returns: The requested contact.
    """
    return await service.get_contact(contact_id, user=current_user)


@router.patch(
    "/{contact_id}",
    status_code=status.HTTP_200_OK,
)
async def update_contact(
    contact_id: int,
    contact: ContactSchema,
    service: ContactService = Depends(contact_service),
    current_user=Depends(get_current_user),
):
    """
    Update a specific contact for the current user.
    Args:
        contact_id (int): The ID of the contact to update.
        contact (ContactSchema): The updated contact data.
        service (ContactService): Contact service dependency.
        current_user: The currently authenticated user.
    Returns: The updated contact.
    """
    return await service.update_contact(contact_id, contact, user=current_user)


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_contact(
    contact_id: int,
    service: ContactService = Depends(contact_service),
    current_user=Depends(get_current_user),
):
    """
    Delete a specific contact for the current user.
    Args:
        contact_id (int): The ID of the contact to delete.
        service (ContactService): Contact service dependency.
        current_user: The currently authenticated user.
    Returns: None
    """
    await service.delete_contact(contact_id, user=current_user)


@router.get(
    "/search/",
    response_model=list[ContactSchema],
    status_code=status.HTTP_200_OK,
)
async def search_contacts(
    name: str | None = Query(None, description="Filter by name"),
    email: str | None = Query(None, description="Filter by email"),
    phone: str | None = Query(None, description="Filter by phone"),
    service: ContactService = Depends(contact_service),
    current_user=Depends(get_current_user),
):
    """
    Search for contacts based on the provided filters.
    Args:
        name (str | None): Filter by name.
        email (str | None): Filter by email.
        phone (str | None): Filter by phone.
        service (ContactService): Contact service dependency.
        current_user: The currently authenticated user.
    Returns: A list of contacts matching the search criteria.
    """
    return await service.search_contacts(name, email, phone, user=current_user)


@router.get(
    "/upcoming-birthdays/",
    response_model=list[ContactSchema],
    status_code=status.HTTP_200_OK,
)
async def get_upcoming_birthdays(
    service: ContactService = Depends(contact_service),
    current_user=Depends(get_current_user),
):
    """
    Get a list of upcoming birthdays for the current user.
    Args:
        service (ContactService): Contact service dependency.
        current_user: The currently authenticated user.
    Returns: A list of contacts with upcoming birthdays.
    """
    return await service.upcoming_birthdays(days=7, user=current_user)
