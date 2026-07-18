from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import ProjectContext
from src.schemas.project_context import ProjectContextUpdate, ProjectContextUpsert


class ProjectContextRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_project_id(self, project_id: UUID) -> ProjectContext | None:
        result = await self.db.execute(
            select(ProjectContext).filter(ProjectContext.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, project_id: UUID, data: ProjectContextUpsert
    ) -> ProjectContext:
        context = ProjectContext(
            project_id=project_id,
            **data.model_dump(),
        )
        self.db.add(context)
        await self.db.commit()
        await self.db.refresh(context)
        return context

    async def update(
        self,
        context: ProjectContext,
        data: ProjectContextUpsert | ProjectContextUpdate,
        *,
        partial: bool = False,
    ) -> ProjectContext:
        payload = (
            data.model_dump(exclude_unset=True) if partial else data.model_dump()
        )
        for field, value in payload.items():
            setattr(context, field, value)
        await self.db.commit()
        await self.db.refresh(context)
        return context
