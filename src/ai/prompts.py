from __future__ import annotations

import json
from typing import TYPE_CHECKING

from src.db.models.enums import GenerationType

if TYPE_CHECKING:
    from src.db.models import ProjectContext, Requirement


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


def build_prompts(
    generation_type: GenerationType,
    requirement: Requirement,
    context: ProjectContext | None,
) -> tuple[str, str]:
    payload = build_request_payload(requirement, context)
    user = (
        "Analyze the following requirement and project context. "
        "Respond with JSON only.\n\n"
        f"{json.dumps(payload, default=str, indent=2)}"
    )

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
