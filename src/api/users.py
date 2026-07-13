from fastapi import (
    APIRouter,
    Depends,
    status,
    Request,
    UploadFile,
    File,
)
from src.db.configurations import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.users import UserUploadAvatarResponceSchema
from src.schemas.auth import UserSchema
from src.db.models import User
from src.services.auth import get_current_user, get_current_admin_user
from src.services.users import UserService
from src.repository.users import UserRepository
from src.conf.limiter import limiter
from src.services.upload_file import UploadFileService
from src.conf.config import config as settings
from src.redis.instance import cache_get, cache_set, redis_client

router = APIRouter(prefix="/users", tags=["users"])


async def user_service(db: AsyncSession = Depends(get_db_session)):
    """
    Dependency to get UserService instance.
    Args:
        db (AsyncSession): Database session dependency.
    Returns: UserService instance.
    """
    repo = UserRepository(db)
    return UserService(repo)


@router.get("/me", response_model=UserSchema)
@limiter.limit("5/minute")
async def me(request: Request, user: UserSchema = Depends(get_current_user)):
    """
    Get the current user's profile information.
    Args:
        request (Request): The HTTP request object.
        user (UserSchema): The currently authenticated user.
    Returns: The current user's profile information.
    """
    cache_key = f"user:{user.id}"
    try:
        cached_user = await cache_get(cache_key, redis_client)
        if cached_user:
            print("🔁 Cache hit!")
            return UserSchema.model_validate(cached_user)

        print("🆕 Cache miss!")
        await cache_set(cache_key, user.model_dump(), 3600, redis_client)
        return user
    except Exception as e:
        print(f"❌ An error with Redis occurred: {e}")
        return user


@router.patch(
    "/avatar",
    status_code=status.HTTP_200_OK,
    response_model=UserUploadAvatarResponceSchema,
)
async def update_user_avatar(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    service: UserService = Depends(user_service),
):
    """
    Update the user's avatar.
    Args:
        file (UploadFile): The uploaded avatar file.
        user (User): The currently authenticated user.
        service (UserService): User service dependency.
    Returns: The updated avatar URL.
    """
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.name)

    user_service = UserService(service)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return UserUploadAvatarResponceSchema(avatar=user.avatar)
