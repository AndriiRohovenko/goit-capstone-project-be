from pydantic import BaseModel, Field, EmailStr
from datetime import date


class ContactSchema(BaseModel):
    name: str = Field(
        ...,
        max_length=50,
        description="Contact's name",
        json_schema_extra={"example": "John Doe"},
    )
    email: EmailStr = Field(
        ...,
        max_length=100,
        description="Contact's email",
        json_schema_extra={"example": "alice@example.com"},
    )
    phone: str = Field(
        ...,
        max_length=20,
        description="Contact's phone number",
        json_schema_extra={"example": "+1234567890"},
    )

    birthdate: date = Field(
        ...,
        description="User's birthdate in YYYY-MM-DD format",
        json_schema_extra={"example": "1990-01-01"},
    )

    model_config = {
        "from_attributes": True,
    }
