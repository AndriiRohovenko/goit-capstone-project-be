from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Requirement
from src.schemas.requirements import RequirementCreate, RequirementUpdate


def _payload_for_orm(data: dict) -> dict:
    if "metadata" in data:
        data["metadata_"] = data.pop("metadata")
    return data


class RequirementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, project_id: UUID, data: RequirementCreate
    ) -> Requirement:
        payload = _payload_for_orm(data.model_dump())
        requirement = Requirement(project_id=project_id, **payload)
        self.db.add(requirement)
        await self.db.commit()
        await self.db.refresh(requirement)
        return requirement

    async def get_by_id(
        self,
        requirement_id: UUID,
        project_id: UUID,
    ) -> Requirement | None:
        result = await self.db.execute(
            select(Requirement).filter(
                Requirement.id == requirement_id,
                Requirement.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_project(
        self,
        project_id: UUID,
        group_id: UUID | None = None,
    ) -> list[Requirement]:
        query = select(Requirement).filter(Requirement.project_id == project_id)
        if group_id is not None:
            query = query.filter(Requirement.group_id == group_id)
        result = await self.db.execute(
            query.order_by(Requirement.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_by_project_and_group(
        self, project_id: UUID, group_id: UUID
    ) -> list[Requirement]:
        result = await self.db.execute(
            select(Requirement)
            .filter(
                Requirement.project_id == project_id,
                Requirement.group_id == group_id,
            )
            .order_by(Requirement.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self, requirement: Requirement, data: RequirementUpdate
    ) -> Requirement:
        payload = _payload_for_orm(data.model_dump(exclude_unset=True))
        for field, value in payload.items():
            setattr(requirement, field, value)
        await self.db.commit()
        await self.db.refresh(requirement)
        return requirement

    async def delete(self, requirement: Requirement) -> None:
        await self.db.delete(requirement)
        await self.db.commit()
