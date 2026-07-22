from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.configurations import get_db_session
from src.exceptions import (
    DuplicateRequirementGroupNameError,
    RequirementGroupNotEmptyError,
    RequirementGroupNotFoundError,
)
from src.repository.requirement_groups import RequirementGroupRepository
from src.schemas.auth import UserSchema
from src.schemas.requirement_groups import (
    RequirementGroupCreate,
    RequirementGroupResponse,
    RequirementGroupUpdate,
)
from src.services.auth import get_current_user


class RequirementGroupService:
    def __init__(
        self,
        group_repository: RequirementGroupRepository,
        user: UserSchema,
    ):
        self.group_repository = group_repository
        self.user = user

    async def create_group(
        self, data: RequirementGroupCreate
    ) -> RequirementGroupResponse:
        existing = await self.group_repository.get_by_name_ci(
            self.user.id, data.name
        )
        if existing:
            raise DuplicateRequirementGroupNameError
        group = await self.group_repository.create(self.user.id, data)
        return RequirementGroupResponse.model_validate(group)

    async def get_all_groups(self) -> list[RequirementGroupResponse]:
        groups = await self.group_repository.get_all_by_owner(self.user.id)
        return [RequirementGroupResponse.model_validate(group) for group in groups]

    async def get_group_by_id(self, group_id: UUID) -> RequirementGroupResponse:
        group = await self.group_repository.get_by_id(group_id, self.user.id)
        if not group:
            raise RequirementGroupNotFoundError
        return RequirementGroupResponse.model_validate(group)

    async def update_group(
        self, group_id: UUID, data: RequirementGroupUpdate
    ) -> RequirementGroupResponse:
        group = await self.group_repository.get_by_id(group_id, self.user.id)
        if not group:
            raise RequirementGroupNotFoundError
        if data.name is not None:
            existing = await self.group_repository.get_by_name_ci(
                self.user.id, data.name
            )
            if existing and existing.id != group.id:
                raise DuplicateRequirementGroupNameError
        updated = await self.group_repository.update(group, data)
        return RequirementGroupResponse.model_validate(updated)

    async def delete_group(self, group_id: UUID) -> None:
        group = await self.group_repository.get_by_id(group_id, self.user.id)
        if not group:
            raise RequirementGroupNotFoundError
        count = await self.group_repository.count_requirements(group_id)
        if count > 0:
            raise RequirementGroupNotEmptyError
        await self.group_repository.delete(group)


def get_requirement_group_service(
    user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> RequirementGroupService:
    return RequirementGroupService(RequirementGroupRepository(db), user)
