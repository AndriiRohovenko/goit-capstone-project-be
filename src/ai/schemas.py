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

REGENERATABLE_ARTIFACT_TYPES = {
    ArtifactType.REQUIREMENT_REVIEW,
    *ALLOWED_TEST_ARTIFACT_TYPES,
}


def parse_requirement_review(
    payload: dict[str, Any],
) -> list[tuple[ArtifactType, dict | list]]:
    parsed = RequirementReviewLLMResponse.model_validate(payload)
    if parsed.artifact_type != ArtifactType.REQUIREMENT_REVIEW:
        raise ValueError(
            "requirement_review response must use artifact_type=requirement_review"
        )
    return [(ArtifactType.REQUIREMENT_REVIEW, parsed.content)]


def parse_test_generation(
    payload: dict[str, Any],
) -> list[tuple[ArtifactType, dict | list]]:
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


class CoveredArea(BaseModel):
    area: str
    requirement_ids: list[str] = Field(default_factory=list)


class PartialArea(BaseModel):
    area: str
    note: str | None = None
    requirement_ids: list[str] = Field(default_factory=list)


class SuggestedRequirement(BaseModel):
    title: str
    description: str = ""
    acceptance_criteria: list[str] = Field(default_factory=list)
    requirement_type: str = "feature"
    priority: str = "medium"


class MissingArea(BaseModel):
    area: str
    risk: str = "medium"
    suggested_requirement: SuggestedRequirement | None = None


class CoverageAnalysisLLMResponse(BaseModel):
    coverage_score: int | None = None
    covered_areas: list[CoveredArea] = Field(default_factory=list)
    partial_areas: list[PartialArea] = Field(default_factory=list)
    missing_areas: list[MissingArea] = Field(default_factory=list)


def parse_coverage_analysis(
    payload: dict[str, Any],
) -> CoverageAnalysisLLMResponse:
    parsed = CoverageAnalysisLLMResponse.model_validate(payload)
    if parsed.coverage_score is not None:
        parsed.coverage_score = max(0, min(100, parsed.coverage_score))
    return parsed


def parse_single_artifact(
    payload: dict[str, Any],
    expected_type: ArtifactType,
) -> list[tuple[ArtifactType, dict | list]]:
    if expected_type == ArtifactType.REQUIREMENT_REVIEW:
        return parse_requirement_review(payload)

    parsed = LLMArtifactItem.model_validate(payload)
    if parsed.artifact_type != expected_type:
        raise ValueError(
            f"expected artifact_type={expected_type.value}, "
            f"got {parsed.artifact_type.value}"
        )
    if parsed.artifact_type not in ALLOWED_TEST_ARTIFACT_TYPES:
        raise ValueError(
            f"unsupported artifact_type for regenerate: {parsed.artifact_type}"
        )
    return [(parsed.artifact_type, parsed.content)]
