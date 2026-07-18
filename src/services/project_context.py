from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.configurations import get_db_session
from src.exceptions import ProjectContextNotFoundError, ProjectNotFoundError
from src.repository.project_context import ProjectContextRepository
from src.repository.projects import ProjectRepository
from src.schemas.auth import UserSchema
from src.schemas.project_context import (
    ProjectContextResponse,
    ProjectContextUpdate,
    ProjectContextUpsert,
)
from src.services.auth import get_current_user


class ProjectContextService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        context_repository: ProjectContextRepository,
        user: UserSchema,
    ):
        self.project_repository = project_repository
        self.context_repository = context_repository
        self.user = user

    async def _require_owned_project(self, project_id: UUID) -> None:
        project = await self.project_repository.get_project_by_id(
            project_id, self.user.id
        )
        if not project:
            raise ProjectNotFoundError

    async def get_context(self, project_id: UUID) -> ProjectContextResponse:
        await self._require_owned_project(project_id)
        context = await self.context_repository.get_by_project_id(project_id)
        if not context:
            raise ProjectContextNotFoundError
        return ProjectContextResponse.model_validate(context)

    async def upsert_context(
        self, project_id: UUID, data: ProjectContextUpsert
    ) -> ProjectContextResponse:
        await self._require_owned_project(project_id)
        context = await self.context_repository.get_by_project_id(project_id)
        if context:
            updated = await self.context_repository.update(
                context, data, partial=False
            )
            return ProjectContextResponse.model_validate(updated)

        created = await self.context_repository.create(project_id, data)
        return ProjectContextResponse.model_validate(created)

    async def patch_context(
        self, project_id: UUID, data: ProjectContextUpdate
    ) -> ProjectContextResponse:
        await self._require_owned_project(project_id)
        context = await self.context_repository.get_by_project_id(project_id)
        if not context:
            raise ProjectContextNotFoundError
        updated = await self.context_repository.update(context, data, partial=True)
        return ProjectContextResponse.model_validate(updated)


def get_project_context_service(
    user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ProjectContextService:
    return ProjectContextService(
        ProjectRepository(db),
        ProjectContextRepository(db),
        user,
    )
