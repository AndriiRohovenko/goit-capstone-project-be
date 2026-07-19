from __future__ import annotations

import json
from typing import TYPE_CHECKING

from src.db.models.enums import ArtifactType, GenerationType

if TYPE_CHECKING:
    from src.db.models import ProjectContext, Requirement

REGENERATABLE_ARTIFACT_TYPES = {
    ArtifactType.REQUIREMENT_REVIEW,
    ArtifactType.TEST_CASES,
    ArtifactType.CHECKLIST,
    ArtifactType.NEGATIVE_SCENARIOS,
    ArtifactType.EDGE_CASES,
}


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
    requirement: Requirement, context: ProjectContext | None
) -> dict:
    return {
        "requirement": _requirement_payload(requirement),
        "project_context": _context_payload(context),
    }


def _user_message(payload: dict) -> str:
    return (
        "Analyze the following requirement and project context. "
        "Respond with JSON only.\n\n"
        f"{json.dumps(payload, default=str, indent=2)}"
    )


def build_prompts(
    generation_type: GenerationType,
    requirement: Requirement,
    context: ProjectContext | None,
) -> tuple[str, str]:
    payload = build_request_payload(requirement, context)
    user = _user_message(payload)

    if generation_type == GenerationType.REQUIREMENT_REVIEW:
        system = (
            "You are a senior QA analyst reviewing software requirements. "
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


def build_regenerate_prompts(
    artifact_type: ArtifactType,
    requirement: Requirement,
    context: ProjectContext | None,
) -> tuple[str, str]:
    if artifact_type not in REGENERATABLE_ARTIFACT_TYPES:
        raise ValueError(f"unsupported artifact_type for regenerate: {artifact_type}")

    payload = build_request_payload(requirement, context)
    user = _user_message(payload)

    if artifact_type == ArtifactType.REQUIREMENT_REVIEW:
        return build_prompts(
            GenerationType.REQUIREMENT_REVIEW, requirement, context
        )

    type_value = artifact_type.value
    content_hint = (
        "a list of objects with title, steps, expected_result, and priority"
        if artifact_type == ArtifactType.TEST_CASES
        else "an object or array with concrete, actionable items"
    )
    system = (
        "You are a senior QA engineer creating a single test design artifact. "
        "Return a single JSON object with this shape:\n"
        "{\n"
        f'  "artifact_type": "{type_value}",\n'
        "  \"content\": object_or_array\n"
        "}\n"
        f"artifact_type must be exactly \"{type_value}\". "
        f"content should be {content_hint}."
    )
    return system, user
