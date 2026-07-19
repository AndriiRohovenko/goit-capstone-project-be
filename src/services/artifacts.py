from uuid import UUID

from fastapi import Depends
from openai import OpenAIError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.client import OpenAIClient
from src.ai.prompts import (
    REGENERATABLE_ARTIFACT_TYPES,
    build_prompts,
    build_regenerate_prompts,
)
from src.ai.schemas import (
    parse_requirement_review,
    parse_single_artifact,
    parse_test_generation,
)
from src.db.configurations import get_db_session
from src.db.models.enums import ArtifactType, GenerationType
from src.exceptions import (
    ArtifactGenerationFailedError,
    ArtifactNotFoundError,
    ProjectNotFoundError,
    RequirementNotFoundError,
    UnsupportedGenerationTypeError,
)
from src.repository.artifacts import ArtifactRepository
from src.repository.project_context import ProjectContextRepository
from src.repository.projects import ProjectRepository
from src.repository.requirements import RequirementRepository
from src.schemas.artifacts import (
    ArtifactGenerateRequest,
    ArtifactResponse,
    ArtifactUpdateRequest,
)
from src.schemas.auth import UserSchema
from src.services.auth import get_current_user


class ArtifactService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        requirement_repository: RequirementRepository,
        context_repository: ProjectContextRepository,
        artifact_repository: ArtifactRepository,
        openai_client: OpenAIClient,
        user: UserSchema,
    ):
        self.project_repository = project_repository
        self.requirement_repository = requirement_repository
        self.context_repository = context_repository
        self.artifact_repository = artifact_repository
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

    async def generate(
        self,
        project_id: UUID,
        requirement_id: UUID,
        data: ArtifactGenerateRequest,
    ) -> list[ArtifactResponse]:
        requirement = await self._require_owned_requirement(
            project_id, requirement_id
        )
        generation_type = GenerationType(data.generation_type)
        if generation_type not in {
            GenerationType.REQUIREMENT_REVIEW,
            GenerationType.TEST_GENERATION,
        }:
            raise UnsupportedGenerationTypeError

        context = await self.context_repository.get_by_project_id(project_id)
        system, user = build_prompts(generation_type, requirement, context)

        try:
            result = await self.openai_client.generate_json(system, user)
            if generation_type == GenerationType.REQUIREMENT_REVIEW:
                artifacts = parse_requirement_review(result.content)
            else:
                artifacts = parse_test_generation(result.content)
        except (OpenAIError, ValidationError, ValueError, TypeError) as exc:
            message = str(exc) or "AI generation failed"
            raise ArtifactGenerationFailedError(message) from exc

        for artifact_type, content in artifacts:
            await self.artifact_repository.upsert(
                requirement_id,
                artifact_type,
                content,
                model=result.model,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                is_edited=False,
            )

        return await self.get_all_artifacts(project_id, requirement_id)

    async def get_all_artifacts(
        self, project_id: UUID, requirement_id: UUID
    ) -> list[ArtifactResponse]:
        await self._require_owned_requirement(project_id, requirement_id)
        artifacts = await self.artifact_repository.get_all_by_requirement(
            requirement_id
        )
        return [
            ArtifactResponse.model_validate(artifact) for artifact in artifacts
        ]

    async def get_artifact_by_type(
        self,
        project_id: UUID,
        requirement_id: UUID,
        artifact_type: ArtifactType,
    ) -> ArtifactResponse:
        await self._require_owned_requirement(project_id, requirement_id)
        artifact = await self.artifact_repository.get_by_type(
            requirement_id, artifact_type
        )
        if not artifact:
            raise ArtifactNotFoundError
        return ArtifactResponse.model_validate(artifact)

    async def update_artifact(
        self,
        project_id: UUID,
        requirement_id: UUID,
        artifact_type: ArtifactType,
        data: ArtifactUpdateRequest,
    ) -> ArtifactResponse:
        await self._require_owned_requirement(project_id, requirement_id)
        artifact = await self.artifact_repository.get_by_type(
            requirement_id, artifact_type
        )
        if not artifact:
            raise ArtifactNotFoundError
        artifact = await self.artifact_repository.update_content(
            artifact, data.content
        )
        return ArtifactResponse.model_validate(artifact)

    async def regenerate(
        self,
        project_id: UUID,
        requirement_id: UUID,
        artifact_type: ArtifactType,
    ) -> ArtifactResponse:
        if artifact_type not in REGENERATABLE_ARTIFACT_TYPES:
            raise UnsupportedGenerationTypeError

        requirement = await self._require_owned_requirement(
            project_id, requirement_id
        )
        context = await self.context_repository.get_by_project_id(project_id)
        system, user = build_regenerate_prompts(
            artifact_type, requirement, context
        )

        try:
            result = await self.openai_client.generate_json(system, user)
            artifacts = parse_single_artifact(result.content, artifact_type)
        except (OpenAIError, ValidationError, ValueError, TypeError) as exc:
            message = str(exc) or "AI generation failed"
            raise ArtifactGenerationFailedError(message) from exc

        parsed_type, content = artifacts[0]
        artifact = await self.artifact_repository.upsert(
            requirement_id,
            parsed_type,
            content,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            is_edited=False,
        )
        return ArtifactResponse.model_validate(artifact)


def get_artifact_service(
    user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ArtifactService:
    return ArtifactService(
        ProjectRepository(db),
        RequirementRepository(db),
        ProjectContextRepository(db),
        ArtifactRepository(db),
        OpenAIClient(),
        user,
    )
