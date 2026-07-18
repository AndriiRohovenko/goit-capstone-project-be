from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.configurations import get_db_session
from src.exceptions import ProjectNotFoundError
from src.repository.projects import ProjectRepository
from src.schemas.auth import UserSchema
from src.schemas.projects import ProjectCreate, ProjectResponse, ProjectUpdate
from src.services.auth import get_current_user


class ProjectService:
    def __init__(self, project_repository: ProjectRepository, user: UserSchema):
        self.project_repository = project_repository
        self.user = user

    async def create_project(self, data: ProjectCreate) -> ProjectResponse:
        project = await self.project_repository.create_project(data, self.user.id)
        return ProjectResponse.model_validate(project)

    async def get_all_projects(self) -> list[ProjectResponse]:
        projects = await self.project_repository.get_all_projects(self.user.id)
        return [ProjectResponse.model_validate(p) for p in projects]

    async def get_project_by_id(self, project_id: UUID) -> ProjectResponse:
        project = await self.project_repository.get_project_by_id(
            project_id, self.user.id
        )
        if not project:
            raise ProjectNotFoundError
        return ProjectResponse.model_validate(project)

    async def update_project(
        self, project_id: UUID, data: ProjectUpdate
    ) -> ProjectResponse:
        project = await self.project_repository.get_project_by_id(
            project_id, self.user.id
        )
        if not project:
            raise ProjectNotFoundError
        updated = await self.project_repository.update_project(project, data)
        return ProjectResponse.model_validate(updated)

    async def delete_project(self, project_id: UUID) -> None:
        project = await self.project_repository.get_project_by_id(
            project_id, self.user.id
        )
        if not project:
            raise ProjectNotFoundError
        await self.project_repository.delete_project(project)


def get_project_service(
    user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ProjectService:
    return ProjectService(ProjectRepository(db), user)
