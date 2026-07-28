from __future__ import annotations

import json
from collections.abc import Sequence
from typing import TYPE_CHECKING

from src.db.models.enums import ArtifactType, GenerationType

if TYPE_CHECKING:
    from src.db.models import GeneratedArtifact, ProjectContext, Requirement

REGENERATABLE_ARTIFACT_TYPES = {
    ArtifactType.REQUIREMENT_REVIEW,
    ArtifactType.TEST_CASES,
    ArtifactType.CHECKLIST,
    ArtifactType.NEGATIVE_SCENARIOS,
    ArtifactType.EDGE_CASES,
}

COVERAGE_ARTIFACT_TYPES = {
    ArtifactType.TEST_CASES,
    ArtifactType.CHECKLIST,
    ArtifactType.NEGATIVE_SCENARIOS,
    ArtifactType.EDGE_CASES,
}

SIBLING_CONTEXT_INSTRUCTION = (
    "sibling_requirements are related requirements in the same group. "
    "Treat them as related scope: do not flag as missing what a sibling "
    "already covers; note overlaps instead. When generating tests, avoid "
    "duplicating scenarios that clearly belong to a sibling."
)

COVERAGE_SIBLING_INSTRUCTION = (
    "Score coverage only against the current requirement and its artifacts. "
    "sibling_requirements are context only: if a gap appears owned by a "
    "sibling, note that under recommendations without changing the score."
)


def _requirement_payload(requirement: Requirement) -> dict:
    return {
        "title": requirement.title,
        "description": requirement.description,
        "acceptance_criteria": requirement.acceptance_criteria,
        "business_rules": requirement.business_rules,
        "requirement_type": requirement.requirement_type,
        "priority": requirement.priority,
        "status": requirement.status,
    }


def _sibling_payload(requirement: Requirement) -> dict:
    return {
        "id": str(requirement.id),
        **_requirement_payload(requirement),
    }


def _context_payload(context: ProjectContext | None) -> dict | None:
    if context is None:
        return None
    return {
        "product_description": context.product_description,
        "domain": context.domain,
        "user_roles": context.user_roles,
        "business_rules": context.business_rules,
        "authentication_type": context.authentication_type,
        "supported_platforms": context.supported_platforms,
        "additional_context": context.additional_context,
    }


def build_request_payload(
    requirement: Requirement,
    context: ProjectContext | None,
    siblings: Sequence[Requirement] = (),
) -> dict:
    return {
        "requirement": _requirement_payload(requirement),
        "project_context": _context_payload(context),
        "sibling_requirements": [
            _sibling_payload(sibling) for sibling in siblings
        ],
    }


def _user_message(payload: dict) -> str:
    return (
        "Analyze the following requirement, project context, and any "
        "sibling requirements in the same group. "
        "Respond with JSON only.\n\n"
        f"{json.dumps(payload, default=str, indent=2)}"
    )


def build_prompts(
    generation_type: GenerationType,
    requirement: Requirement,
    context: ProjectContext | None,
    siblings: Sequence[Requirement] = (),
) -> tuple[str, str]:
    payload = build_request_payload(requirement, context, siblings)
    user = _user_message(payload)

    if generation_type == GenerationType.REQUIREMENT_REVIEW:
        system = (
            "You are a senior QA analyst reviewing software requirements. "
            f"{SIBLING_CONTEXT_INSTRUCTION} "
            "Return a single JSON object with this shape:\n"
            "{\n"
            '  "artifact_type": "requirement_review",\n'
            '  "content": {\n'
            '    "summary": string,\n'
            '    "quality_issues": [string],\n'
            '    "ambiguities": [string],\n'
            '    "missing_details": [string],\n'
            '    "suggestions": [string]\n'
            "  }\n"
            "}\n"
            "Be concrete and actionable."
        )
        return system, user

    if generation_type == GenerationType.TEST_GENERATION:
        system = (
            "You are a senior QA engineer creating test design artifacts. "
            f"{SIBLING_CONTEXT_INSTRUCTION} "
            "Return a single JSON object with this shape:\n"
            "{\n"
            '  "artifacts": [\n'
            "    {\n"
            '      "artifact_type": "test_cases" | "checklist" | '
            '"negative_scenarios" | "edge_cases",\n'
            '      "content": object_or_array\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Include at least one artifact. Prefer multiple types when useful. "
            "For test_cases, content should be a list of objects with "
            "title, steps, expected_result, and priority."
        )
        return system, user

    raise ValueError(f"unsupported generation_type: {generation_type}")


def _artifact_payload(artifact: GeneratedArtifact) -> dict:
    return {
        "artifact_type": artifact.artifact_type,
        "content": artifact.content,
        "is_edited": artifact.is_edited,
    }


def build_coverage_payload(
    requirement: Requirement,
    artifacts: list[GeneratedArtifact],
    context: ProjectContext | None,
    siblings: Sequence[Requirement] = (),
) -> dict:
    return {
        "requirement": {
            "id": str(requirement.id),
            **_requirement_payload(requirement),
        },
        "artifacts": [_artifact_payload(artifact) for artifact in artifacts],
        "project_context": _context_payload(context),
        "sibling_requirements": [
            _sibling_payload(sibling) for sibling in siblings
        ],
    }


def build_coverage_prompts(
    requirement: Requirement,
    artifacts: list[GeneratedArtifact],
    context: ProjectContext | None,
    siblings: Sequence[Requirement] = (),
) -> tuple[str, str]:
    payload = build_coverage_payload(
        requirement, artifacts, context, siblings
    )
    user = (
        "Analyze how well the generated test design artifacts cover the "
        "requirement below (including acceptance criteria and business rules). "
        "Identify covered, partially covered, and missing scenarios. "
        "Respond with JSON only.\n\n"
        f"{json.dumps(payload, default=str, indent=2)}"
    )
    system = (
        "You are a senior QA analyst assessing test coverage of a single "
        "software requirement based on its generated test artifacts. "
        "Compare the requirement against the provided artifacts "
        "(test_cases, checklist, negative_scenarios, edge_cases). "
        f"{COVERAGE_SIBLING_INSTRUCTION} "
        "Return a single JSON object with this shape:\n"
        "{\n"
        '  "coverage_score": number (0-100),\n'
        '  "covered_areas": [\n'
        '    { "area": string, "artifact_refs": [string] }\n'
        "  ],\n"
        '  "partial_areas": [\n'
        '    { "area": string, "note": string, "artifact_refs": [string] }\n'
        "  ],\n"
        '  "missing_scenarios": [\n'
        "    {\n"
        '      "area": string,\n'
        '      "risk": "low" | "medium" | "high",\n'
        '      "scenario_type": "negative" | "edge" | "security" | '
        '"accessibility" | "functional" | "other",\n'
        '      "suggested_artifact": {\n'
        '        "artifact_type": "test_cases" | "checklist" | '
        '"negative_scenarios" | "edge_cases",\n'
        '        "title": string,\n'
        '        "steps_or_items": [string],\n'
        '        "expected_result": string\n'
        "      }\n"
        "    }\n"
        "  ],\n"
        '  "recommendations": [\n'
        "    {\n"
        '      "category": "missing_edge_cases" | "automation_priority" | '
        '"risk" | "requirement_quality" | "other",\n'
        '      "priority": "low" | "medium" | "high",\n'
        '      "text": string\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "coverage_score reflects how completely the artifacts cover the "
        "requirement. artifact_refs should reference provided artifacts "
        '(e.g. "test_cases#0"). Be concrete and actionable.'
    )
    return system, user


def build_regenerate_prompts(
    artifact_type: ArtifactType,
    requirement: Requirement,
    context: ProjectContext | None,
    siblings: Sequence[Requirement] = (),
) -> tuple[str, str]:
    if artifact_type not in REGENERATABLE_ARTIFACT_TYPES:
        raise ValueError(f"unsupported artifact_type for regenerate: {artifact_type}")

    if artifact_type == ArtifactType.REQUIREMENT_REVIEW:
        return build_prompts(
            GenerationType.REQUIREMENT_REVIEW,
            requirement,
            context,
            siblings,
        )

    payload = build_request_payload(requirement, context, siblings)
    user = _user_message(payload)

    type_value = artifact_type.value
    content_hint = (
        "a list of objects with title, steps, expected_result, and priority"
        if artifact_type == ArtifactType.TEST_CASES
        else "an object or array with concrete, actionable items"
    )
    system = (
        "You are a senior QA engineer creating a single test design artifact. "
        f"{SIBLING_CONTEXT_INSTRUCTION} "
        "Return a single JSON object with this shape:\n"
        "{\n"
        f'  "artifact_type": "{type_value}",\n'
        "  \"content\": object_or_array\n"
        "}\n"
        f"artifact_type must be exactly \"{type_value}\". "
        f"content should be {content_hint}."
    )
    return system, user
