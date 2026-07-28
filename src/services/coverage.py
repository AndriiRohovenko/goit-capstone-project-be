from uuid import UUID

from fastapi import Depends
from openai import OpenAIError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.client import OpenAIClient
from src.ai.prompts import COVERAGE_ARTIFACT_TYPES, build_coverage_prompts
from src.ai.schemas import parse_coverage_analysis
from src.db.configurations import get_db_session
from src.db.models import Requirement
from src.exceptions import (
    ArtifactGenerationFailedError,
    ArtifactsRequiredForCoverageError,
    CoverageReportNotFoundError,
    ProjectNotFoundError,
    RequirementNotFoundError,
)
from src.repository.artifacts import ArtifactRepository
from src.repository.coverage_reports import CoverageReportRepository
from src.repository.project_context import ProjectContextRepository
from src.repository.projects import ProjectRepository
from src.repository.requirements import RequirementRepository
from src.schemas.auth import UserSchema
from src.schemas.coverage import CoverageReportResponse
from src.services.auth import get_current_user


class CoverageService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        requirement_repository: RequirementRepository,
        artifact_repository: ArtifactRepository,
        context_repository: ProjectContextRepository,
        coverage_repository: CoverageReportRepository,
        openai_client: OpenAIClient,
        user: UserSchema,
    ):
        self.project_repository = project_repository
        self.requirement_repository = requirement_repository
        self.artifact_repository = artifact_repository
        self.context_repository = context_repository
        self.coverage_repository = coverage_repository
        self.openai_client = openai_client
        self.user = user

    async def _require_owned_requirement(
        self, project_id: UUID, requirement_id: UUID
    ):
        project = await self.project_repository.get_project_by_id(
            project_id, self.user.id
        )
        if not project:
            raise ProjectNotFoundError

        requirement = await self.requirement_repository.get_by_id(
            requirement_id, project_id
        )
        if not requirement:
            raise RequirementNotFoundError
        return requirement

    async def _sibling_requirements(
        self, project_id: UUID, requirement: Requirement
    ) -> list[Requirement]:
        if requirement.group_id is None:
            return []
        group_reqs = await self.requirement_repository.get_all_by_project_and_group(
            project_id, requirement.group_id
        )
        return [r for r in group_reqs if r.id != requirement.id][:20]

    async def analyze(
        self, project_id: UUID, requirement_id: UUID
    ) -> CoverageReportResponse:
        requirement = await self._require_owned_requirement(
            project_id, requirement_id
        )
        artifacts = await self.artifact_repository.get_all_by_requirement(
            requirement_id
        )
        test_artifacts = [
            artifact
            for artifact in artifacts
            if artifact.artifact_type in COVERAGE_ARTIFACT_TYPES
        ]
        if not test_artifacts:
            raise ArtifactsRequiredForCoverageError

        context = await self.context_repository.get_by_project_id(project_id)
        siblings = await self._sibling_requirements(project_id, requirement)
        system, user = build_coverage_prompts(
            requirement, test_artifacts, context, siblings
        )

        try:
            result = await self.openai_client.generate_json(system, user)
            parsed = parse_coverage_analysis(result.content)
        except (OpenAIError, ValidationError, ValueError, TypeError) as exc:
            message = str(exc) or "AI generation failed"
            raise ArtifactGenerationFailedError(message) from exc

        report = await self.coverage_repository.upsert(
            project_id,
            requirement_id,
            parsed.model_dump(exclude={"coverage_score"}),
            coverage_score=parsed.coverage_score,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )
        return CoverageReportResponse.model_validate(report)

    async def get_report(
        self, project_id: UUID, requirement_id: UUID
    ) -> CoverageReportResponse:
        await self._require_owned_requirement(project_id, requirement_id)
        report = await self.coverage_repository.get_by_requirement_id(
            requirement_id
        )
        if not report:
            raise CoverageReportNotFoundError
        return CoverageReportResponse.model_validate(report)


def get_coverage_service(
    user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> CoverageService:
    return CoverageService(
        ProjectRepository(db),
        RequirementRepository(db),
        ArtifactRepository(db),
        ProjectContextRepository(db),
        CoverageReportRepository(db),
        OpenAIClient(),
        user,
    )
