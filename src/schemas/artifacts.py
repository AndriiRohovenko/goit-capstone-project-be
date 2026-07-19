from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.db.models.enums import ArtifactType

AllowedGenerationType = Literal["requirement_review", "test_generation"]


class ArtifactGenerateRequest(BaseModel):
    generation_type: AllowedGenerationType


class ArtifactUpdateRequest(BaseModel):
    content: dict | list


class ArtifactResponse(BaseModel):
    id: UUID
    requirement_id: UUID
    artifact_type: ArtifactType
    content: dict | list
    is_edited: bool
    model: str | None
    input_tokens: int | None
    output_tokens: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
