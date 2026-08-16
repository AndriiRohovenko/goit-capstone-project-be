from fastapi import APIRouter, Depends, File, UploadFile, status

from src.conf.config import config as settings
from src.schemas.auth import UserSchema
from src.schemas.users import UserUploadAvatarResponceSchema
from src.services.auth import get_current_user
from src.services.dependencies import get_user_service
from src.services.upload_file import UploadFileService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
async def me(user: UserSchema = Depends(get_current_user)):
    try:
        return UserSchema.model_validate(user.model_dump())
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
