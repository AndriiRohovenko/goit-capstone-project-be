from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from src.conf.config import config as settings
from src.conf.limiter import limiter
from src.redis.instance import cache_get, cache_set, redis_client
from src.schemas.auth import UserSchema
from src.schemas.users import UserUploadAvatarResponceSchema
from src.services.auth import get_current_user
from src.services.dependencies import get_user_service
from src.services.upload_file import UploadFileService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
@limiter.limit("5/minute")
async def me(request: Request, user: UserSchema = Depends(get_current_user)):
    cache_key = f"user:{user.id}"
    try:
        cached_user = await cache_get(cache_key, redis_client)
        if cached_user:
            return UserSchema.model_validate(cached_user)

        await cache_set(cache_key, user.model_dump(), 3600, redis_client)
        return user
    except Exception:
        return user


@router.patch(
    "/avatar",
    status_code=status.HTTP_200_OK,
    response_model=UserUploadAvatarResponceSchema,
)
async def update_user_avatar(
    file: UploadFile = File(),
    user: UserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.name)

    updated = await service.update_avatar_url(user.email, avatar_url)
    return UserUploadAvatarResponceSchema(avatar=updated.avatar)
