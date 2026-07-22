from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CoverageReportResponse(BaseModel):
    id: UUID
    project_id: UUID
    group_id: UUID
    content: dict | list
    coverage_score: int | None
    model: str | None
    input_tokens: int | None
    output_tokens: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
