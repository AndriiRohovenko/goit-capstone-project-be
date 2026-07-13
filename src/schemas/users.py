from pydantic import BaseModel, Field
from typing import Optional


class UserUploadAvatarResponceSchema(BaseModel):
    avatar: Optional[str] = Field(
        None,
        description="URL of the user's avatar image",
        json_schema_extra={"example": "https://example.com/avatars/johndoe.jpg"},
    )
