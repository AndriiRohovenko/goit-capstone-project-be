from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectContextUpsert(BaseModel):
    product_description: str | None = None
    domain: str | None = Field(None, max_length=100)
    user_roles: list[str] = Field(default_factory=list)
    business_rules: list[str] = Field(default_factory=list)
    authentication_type: str | None = Field(None, max_length=100)
    supported_platforms: list[str] = Field(default_factory=list)
    additional_context: dict = Field(default_factory=dict)


class ProjectContextUpdate(BaseModel):
    product_description: str | None = None
    domain: str | None = Field(None, max_length=100)
    user_roles: list[str] | None = None
    business_rules: list[str] | None = None
    authentication_type: str | None = Field(None, max_length=100)
    supported_platforms: list[str] | None = None
    additional_context: dict | None = None


class ProjectContextResponse(BaseModel):
    id: UUID
    project_id: UUID
    product_description: str | None
    domain: str | None
    user_roles: list[str]
    business_rules: list[str]
    authentication_type: str | None
    supported_platforms: list[str]
    additional_context: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
