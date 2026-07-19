from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import AIGeneration, GeneratedArtifact
from src.db.models.enums import ArtifactType, GenerationStatus, GenerationType


class GenerationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        requirement_id: UUID,
        generation_type: GenerationType,
        model: str,
        request_payload: dict,
        prompt_version: str = "v1",
    ) -> AIGeneration:
        generation = AIGeneration(
            requirement_id=requirement_id,
            generation_type=generation_type,
            status=GenerationStatus.PENDING,
            model=model,
            prompt_version=prompt_version,
            request_payload=request_payload,
        )
        self.db.add(generation)
        await self.db.commit()
        await self.db.refresh(generation)
        return generation

    async def get_by_id(
        self, generation_id: UUID, requirement_id: UUID
    ) -> AIGeneration | None:
        result = await self.db.execute(
            select(AIGeneration)
            .options(selectinload(AIGeneration.artifacts))
            .filter(
                AIGeneration.id == generation_id,
                AIGeneration.requirement_id == requirement_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_requirement(
        self, requirement_id: UUID
    ) -> list[AIGeneration]:
        result = await self.db.execute(
            select(AIGeneration)
            .options(selectinload(AIGeneration.artifacts))
            .filter(AIGeneration.requirement_id == requirement_id)
            .order_by(AIGeneration.created_at.desc())
        )
        return list(result.scalars().all())

    async def mark_processing(self, generation: AIGeneration) -> AIGeneration:
        generation.status = GenerationStatus.PROCESSING
        await self.db.commit()
        await self.db.refresh(generation)
        return generation

    async def complete(
        self,
        generation: AIGeneration,
        *,
        input_tokens: int | None,
        output_tokens: int | None,
        artifacts: list[tuple[ArtifactType, dict | list]],
        estimated_cost: Decimal | None = None,
        model: str | None = None,
    ) -> AIGeneration:
        # Capture before commit — expire_on_commit would make .id lazy-load.
        generation_id = generation.id

        generation.status = GenerationStatus.COMPLETED
        generation.input_tokens = input_tokens
        generation.output_tokens = output_tokens
        generation.estimated_cost = estimated_cost
        generation.completed_at = datetime.now(timezone.utc)
        generation.error_message = None
        if model:
            generation.model = model

        for artifact_type, content in artifacts:
            self.db.add(
                GeneratedArtifact(
                    generation_id=generation_id,
                    artifact_type=artifact_type,
                    content=content,
                )
            )

        await self.db.commit()
        result = await self.db.execute(
            select(AIGeneration)
            .options(selectinload(AIGeneration.artifacts))
            .filter(AIGeneration.id == generation_id)
        )
        return result.scalar_one()

    async def fail(
        self, generation: AIGeneration, error_message: str
    ) -> AIGeneration:
        generation_id = generation.id
        generation.status = GenerationStatus.FAILED
        generation.error_message = error_message
        generation.completed_at = datetime.now(timezone.utc)
        await self.db.commit()
        result = await self.db.execute(
            select(AIGeneration).filter(AIGeneration.id == generation_id)
        )
        return result.scalar_one()
