from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import GeneratedArtifact
from src.db.models.enums import ArtifactType


class ArtifactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_by_requirement(
        self, requirement_id: UUID
    ) -> list[GeneratedArtifact]:
        result = await self.db.execute(
            select(GeneratedArtifact)
            .filter(GeneratedArtifact.requirement_id == requirement_id)
            .order_by(GeneratedArtifact.artifact_type)
        )
        return list(result.scalars().all())

    async def get_by_type(
        self, requirement_id: UUID, artifact_type: ArtifactType
    ) -> GeneratedArtifact | None:
        result = await self.db.execute(
            select(GeneratedArtifact).filter(
                GeneratedArtifact.requirement_id == requirement_id,
                GeneratedArtifact.artifact_type == artifact_type,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        requirement_id: UUID,
        artifact_type: ArtifactType,
        content: dict | list,
        *,
        model: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        is_edited: bool = False,
    ) -> GeneratedArtifact:
        artifact = await self.get_by_type(requirement_id, artifact_type)
        if artifact is None:
            artifact = GeneratedArtifact(
                requirement_id=requirement_id,
                artifact_type=artifact_type,
                content=content,
                is_edited=is_edited,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            self.db.add(artifact)
        else:
            artifact.content = content
            artifact.is_edited = is_edited
            artifact.model = model
            artifact.input_tokens = input_tokens
            artifact.output_tokens = output_tokens

        await self.db.commit()
        await self.db.refresh(artifact)
        return artifact

    async def update_content(
        self,
        artifact: GeneratedArtifact,
        content: dict | list,
    ) -> GeneratedArtifact:
        artifact.content = content
        artifact.is_edited = True
        await self.db.commit()
        await self.db.refresh(artifact)
        return artifact
