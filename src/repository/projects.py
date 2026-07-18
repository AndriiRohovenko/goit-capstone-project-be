from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Project
from src.schemas.projects import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, data: ProjectCreate, owner_id: UUID) -> Project:
        project = Project(
            name=data.name,
            description=data.description,
            owner_id=owner_id,
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_project_by_id(
        self, project_id: UUID, owner_id: UUID
    ) -> Project | None:
        result = await self.db.execute(
            select(Project).filter(
                Project.id == project_id,
                Project.owner_id == owner_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_projects(self, owner_id: UUID) -> list[Project]:
        result = await self.db.execute(
            select(Project)
            .filter(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_project(
        self, project: Project, project_data: ProjectUpdate
    ) -> Project:
        for field, value in project_data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project: Project) -> None:
        await self.db.delete(project)
        await self.db.commit()
