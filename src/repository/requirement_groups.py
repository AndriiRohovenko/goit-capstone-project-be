from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Requirement, RequirementGroup
from src.schemas.requirement_groups import (
    RequirementGroupCreate,
    RequirementGroupUpdate,
)


class RequirementGroupRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, owner_id: UUID, data: RequirementGroupCreate
    ) -> RequirementGroup:
        group = RequirementGroup(owner_id=owner_id, **data.model_dump())
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def get_by_id(
        self, group_id: UUID, owner_id: UUID
    ) -> RequirementGroup | None:
        result = await self.db.execute(
            select(RequirementGroup).filter(
                RequirementGroup.id == group_id,
                RequirementGroup.owner_id == owner_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_owner(self, owner_id: UUID) -> list[RequirementGroup]:
        result = await self.db.execute(
            select(RequirementGroup)
            .filter(RequirementGroup.owner_id == owner_id)
            .order_by(RequirementGroup.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_requirements(self, group_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Requirement)
            .filter(Requirement.group_id == group_id)
        )
        return int(result.scalar_one())

    async def update(
        self, group: RequirementGroup, data: RequirementGroupUpdate
    ) -> RequirementGroup:
        payload = data.model_dump(exclude_unset=True)
        for field, value in payload.items():
            setattr(group, field, value)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def delete(self, group: RequirementGroup) -> None:
        await self.db.delete(group)
        await self.db.commit()
