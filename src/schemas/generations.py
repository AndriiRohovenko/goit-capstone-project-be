from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.db.models.enums import ArtifactType, GenerationStatus, GenerationType

AllowedGenerationType = Literal["requirement_review", "test_generation"]


class GenerationCreate(BaseModel):
    generation_type: AllowedGenerationType


class GeneratedArtifactResponse(BaseModel):
    id: UUID
    generation_id: UUID
    artifact_type: ArtifactType
    content: dict | list
    version: int
    is_edited: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GenerationResponse(BaseModel):
    id: UUID
    requirement_id: UUID
    generation_type: GenerationType
    status: GenerationStatus
    model: str
    prompt_version: str
    request_payload: dict
    input_tokens: int | None
    output_tokens: int | None
    estimated_cost: Decimal | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None
    artifacts: list[GeneratedArtifactResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
