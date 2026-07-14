from pydantic import BaseModel, Field, EmailStr, ConfigDict
from uuid import UUID


class UserSchema(BaseModel):
    id: UUID
    name: str
    surname: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    old_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)
