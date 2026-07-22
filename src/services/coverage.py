from uuid import UUID

from fastapi import Depends
from openai import OpenAIError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.client import OpenAIClient
from src.ai.prompts import build_coverage_prompts
from src.ai.schemas import parse_coverage_analysis
from src.db.configurations import get_db_session
from src.exceptions import (
    ArtifactGenerationFailedError,
    CoverageReportNotFoundError,
    ProjectNotFoundError,
    RequirementGroupNotFoundError,
)
from src.repository.coverage_reports import CoverageReportRepository
from src.repository.project_context import ProjectContextRepository
from src.repository.projects import ProjectRepository
from src.repository.requirement_groups import RequirementGroupRepository
from src.repository.requirements import RequirementRepository
from src.schemas.auth import UserSchema
from src.schemas.coverage import CoverageReportResponse
from src.services.auth import get_current_user


class CoverageService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        group_repository: RequirementGroupRepository,
        requirement_repository: RequirementRepository,
        context_repository: ProjectContextRepository,
        coverage_repository: CoverageReportRepository,
        openai_client: OpenAIClient,
        user: UserSchema,
    ):
        self.project_repository = project_repository
        self.group_repository = group_repository
        self.requirement_repository = requirement_repository
        self.context_repository = context_repository
        self.coverage_repository = coverage_repository
        self.openai_client = openai_client
        self.user = user

    async def _require_owned_project(self, project_id: UUID):
        project = await self.project_repository.get_project_by_id(
            project_id, self.user.id
        )
        if not project:
            raise ProjectNotFoundError
        return project

    async def _require_owned_group(self, group_id: UUID):
        group = await self.group_repository.get_by_id(group_id, self.user.id)
        if not group:
            raise RequirementGroupNotFoundError
        return group

    async def analyze(
        self, project_id: UUID, group_id: UUID
    ) -> CoverageReportResponse:
        await self._require_owned_project(project_id)
        group = await self._require_owned_group(group_id)

        requirements = (
            await self.requirement_repository.get_all_by_project_and_group(
                project_id, group_id
            )
        )
        context = await self.context_repository.get_by_project_id(project_id)
        system, user = build_coverage_prompts(group, requirements, context)

        try:
            result = await self.openai_client.generate_json(system, user)
            parsed = parse_coverage_analysis(result.content)
        except (OpenAIError, ValidationError, ValueError, TypeError) as exc:
            message = str(exc) or "AI generation failed"
            raise ArtifactGenerationFailedError(message) from exc

        report = await self.coverage_repository.upsert(
            project_id,
            group_id,
            parsed.model_dump(exclude={"coverage_score"}),
            coverage_score=parsed.coverage_score,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )
        return CoverageReportResponse.model_validate(report)

    async def analyze_all(
        self, project_id: UUID
    ) -> list[CoverageReportResponse]:
        await self._require_owned_project(project_id)
        groups = await self.group_repository.get_all_by_owner(self.user.id)

        reports: list[CoverageReportResponse] = []
        for group in groups:
            reports.append(await self.analyze(project_id, group.id))
        return reports

    async def get_report(
        self, project_id: UUID, group_id: UUID
    ) -> CoverageReportResponse:
        await self._require_owned_project(project_id)
        await self._require_owned_group(group_id)
        report = await self.coverage_repository.get_by_project_group(
            project_id, group_id
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
        RequirementGroupRepository(db),
        RequirementRepository(db),
        ProjectContextRepository(db),
        CoverageReportRepository(db),
        OpenAIClient(),
        user,
    )
