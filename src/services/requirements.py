from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.configurations import get_db_session
from src.exceptions import ProjectNotFoundError, RequirementNotFoundError
from src.repository.projects import ProjectRepository
from src.repository.requirements import RequirementRepository
from src.schemas.auth import UserSchema
from src.schemas.requirements import (
    RequirementCreate,
    RequirementResponse,
    RequirementUpdate,
)
from src.services.auth import get_current_user


class RequirementService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        requirement_repository: RequirementRepository,
        user: UserSchema,
    ):
        self.project_repository = project_repository
        self.requirement_repository = requirement_repository
        self.user = user

    async def _require_owned_project(self, project_id: UUID) -> None:
        project = await self.project_repository.get_project_by_id(
            project_id, self.user.id
        )
        if not project:
            raise ProjectNotFoundError

    async def create_requirement(
        self, project_id: UUID, data: RequirementCreate
    ) -> RequirementResponse:
        await self._require_owned_project(project_id)
        requirement = await self.requirement_repository.create(project_id, data)
        return RequirementResponse.model_validate(requirement)

    async def get_all_requirements(
        self, project_id: UUID
    ) -> list[RequirementResponse]:
        await self._require_owned_project(project_id)
        requirements = await self.requirement_repository.get_all_by_project(
            project_id
        )
        return [
            RequirementResponse.model_validate(requirement)
            for requirement in requirements
        ]

    async def get_requirement_by_id(
        self, project_id: UUID, requirement_id: UUID
    ) -> RequirementResponse:
        await self._require_owned_project(project_id)
        requirement = await self.requirement_repository.get_by_id(
            requirement_id, project_id
        )
        if not requirement:
            raise RequirementNotFoundError
        return RequirementResponse.model_validate(requirement)

    async def update_requirement(
        self,
        project_id: UUID,
        requirement_id: UUID,
        data: RequirementUpdate,
    ) -> RequirementResponse:
        await self._require_owned_project(project_id)
        requirement = await self.requirement_repository.get_by_id(
            requirement_id, project_id
        )
        if not requirement:
            raise RequirementNotFoundError
        updated = await self.requirement_repository.update(requirement, data)
        return RequirementResponse.model_validate(updated)

    async def delete_requirement(
        self, project_id: UUID, requirement_id: UUID
    ) -> None:
        await self._require_owned_project(project_id)
        requirement = await self.requirement_repository.get_by_id(
            requirement_id, project_id
        )
        if not requirement:
            raise RequirementNotFoundError
        await self.requirement_repository.delete(requirement)


def get_requirement_service(
    user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> RequirementService:
    return RequirementService(
        ProjectRepository(db),
        RequirementRepository(db),
        user,
    )
