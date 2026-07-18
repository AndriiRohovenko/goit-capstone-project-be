from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.db.models.enums import ProjectStatus


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = Field(None, max_length=255)


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=150)
    description: str | None = Field(None, max_length=255)
    status: ProjectStatus | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
