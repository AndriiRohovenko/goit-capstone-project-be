from uuid import UUID

from fastapi import Depends
from openai import OpenAIError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.client import OpenAIClient
from src.ai.prompts import build_prompts, build_request_payload
from src.ai.schemas import parse_requirement_review, parse_test_generation
from src.conf.config import config
from src.db.configurations import get_db_session
from src.db.models.enums import GenerationType
from src.exceptions import (
    GenerationFailedError,
    GenerationNotFoundError,
    ProjectNotFoundError,
    RequirementNotFoundError,
    UnsupportedGenerationTypeError,
)
from src.repository.generations import GenerationRepository
from src.repository.project_context import ProjectContextRepository
from src.repository.projects import ProjectRepository
from src.repository.requirements import RequirementRepository
from src.schemas.auth import UserSchema
from src.schemas.generations import GenerationCreate, GenerationResponse
from src.services.auth import get_current_user


class GenerationService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        requirement_repository: RequirementRepository,
        context_repository: ProjectContextRepository,
        generation_repository: GenerationRepository,
        openai_client: OpenAIClient,
        user: UserSchema,
    ):
        self.project_repository = project_repository
        self.requirement_repository = requirement_repository
        self.context_repository = context_repository
        self.generation_repository = generation_repository
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

    async def create_generation(
        self,
        project_id: UUID,
        requirement_id: UUID,
        data: GenerationCreate,
    ) -> GenerationResponse:
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
        request_payload = build_request_payload(requirement, context)
        # Build before commit so expired ORM attrs are not lazy-loaded.
        system, user = build_prompts(generation_type, requirement, context)

        generation = await self.generation_repository.create(
            requirement_id=requirement_id,
            generation_type=generation_type,
            model=config.OPENAI_MODEL,
            request_payload=request_payload,
        )
        generation = await self.generation_repository.mark_processing(generation)

        try:
            result = await self.openai_client.generate_json(system, user)

            if generation_type == GenerationType.REQUIREMENT_REVIEW:
                artifacts = parse_requirement_review(result.content)
            else:
                artifacts = parse_test_generation(result.content)

            generation = await self.generation_repository.complete(
                generation,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                artifacts=artifacts,
                model=result.model,
            )
        except (OpenAIError, ValidationError, ValueError, TypeError) as exc:
            message = str(exc) or "AI generation failed"
            await self.generation_repository.fail(generation, message)
            raise GenerationFailedError(message) from exc

        return GenerationResponse.model_validate(generation)

    async def get_all_generations(
        self, project_id: UUID, requirement_id: UUID
    ) -> list[GenerationResponse]:
        await self._require_owned_requirement(project_id, requirement_id)
        generations = await self.generation_repository.get_all_by_requirement(
            requirement_id
        )
        return [
            GenerationResponse.model_validate(generation)
            for generation in generations
        ]

    async def get_generation_by_id(
        self,
        project_id: UUID,
        requirement_id: UUID,
        generation_id: UUID,
    ) -> GenerationResponse:
        await self._require_owned_requirement(project_id, requirement_id)
        generation = await self.generation_repository.get_by_id(
            generation_id, requirement_id
        )
        if not generation:
            raise GenerationNotFoundError
        return GenerationResponse.model_validate(generation)


def get_generation_service(
    user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> GenerationService:
    return GenerationService(
        ProjectRepository(db),
        RequirementRepository(db),
        ProjectContextRepository(db),
        GenerationRepository(db),
        OpenAIClient(),
        user,
    )
