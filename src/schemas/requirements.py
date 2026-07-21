from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.db.models.enums import (
    RequirementPriority,
    RequirementStatus,
    RequirementType,
)


class RequirementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=250)
    description: str = Field(..., min_length=1)
    group_id: UUID
    acceptance_criteria: list[str] = Field(default_factory=list)
    business_rules: list[str] = Field(default_factory=list)
    requirement_type: RequirementType = RequirementType.USER_STORY
    priority: RequirementPriority = RequirementPriority.MEDIUM
    status: RequirementStatus = RequirementStatus.DRAFT
    metadata: dict = Field(default_factory=dict)


class RequirementUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=250)
    description: str | None = Field(None, min_length=1)
    group_id: UUID | None = None
    acceptance_criteria: list[str] | None = None
    business_rules: list[str] | None = None
    requirement_type: RequirementType | None = None
    priority: RequirementPriority | None = None
    status: RequirementStatus | None = None
    metadata: dict | None = None


class RequirementResponse(BaseModel):
    id: UUID
    project_id: UUID
    group_id: UUID
    title: str
    description: str
    acceptance_criteria: list[str]
    business_rules: list[str]
    requirement_type: RequirementType
    priority: RequirementPriority
    status: RequirementStatus
    metadata: dict = Field(validation_alias="metadata_")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
