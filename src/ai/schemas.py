from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.db.models.enums import ArtifactType


class LLMArtifactItem(BaseModel):
    artifact_type: ArtifactType
    content: dict | list


class RequirementReviewLLMResponse(BaseModel):
    artifact_type: ArtifactType = ArtifactType.REQUIREMENT_REVIEW
    content: dict = Field(default_factory=dict)


class TestGenerationLLMResponse(BaseModel):
    artifacts: list[LLMArtifactItem] = Field(default_factory=list)


ALLOWED_TEST_ARTIFACT_TYPES = {
    ArtifactType.TEST_CASES,
    ArtifactType.CHECKLIST,
    ArtifactType.NEGATIVE_SCENARIOS,
    ArtifactType.EDGE_CASES,
}


def parse_requirement_review(payload: dict[str, Any]) -> list[tuple[ArtifactType, dict | list]]:
    parsed = RequirementReviewLLMResponse.model_validate(payload)
    if parsed.artifact_type != ArtifactType.REQUIREMENT_REVIEW:
        raise ValueError("requirement_review response must use artifact_type=requirement_review")
    return [(ArtifactType.REQUIREMENT_REVIEW, parsed.content)]


def parse_test_generation(payload: dict[str, Any]) -> list[tuple[ArtifactType, dict | list]]:
    parsed = TestGenerationLLMResponse.model_validate(payload)
    if not parsed.artifacts:
        raise ValueError("test_generation response must include at least one artifact")

    results: list[tuple[ArtifactType, dict | list]] = []
    for item in parsed.artifacts:
        if item.artifact_type not in ALLOWED_TEST_ARTIFACT_TYPES:
            raise ValueError(
                f"unsupported artifact_type for test_generation: {item.artifact_type}"
            )
        results.append((item.artifact_type, item.content))
    return results
