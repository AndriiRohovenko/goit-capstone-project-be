from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RequirementGroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = None


class RequirementGroupUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    description: str | None = None


class RequirementGroupResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
