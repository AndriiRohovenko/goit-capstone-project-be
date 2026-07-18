from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.schemas.project_context import (
    ProjectContextResponse,
    ProjectContextUpdate,
    ProjectContextUpsert,
)
from src.schemas.projects import ProjectCreate, ProjectResponse, ProjectUpdate
from src.services.project_context import (
    ProjectContextService,
    get_project_context_service,
)
from src.services.projects import ProjectService, get_project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
):
    return await project_service.create_project(project)


@router.get("/", response_model=list[ProjectResponse])
async def get_all_projects(
    project_service: ProjectService = Depends(get_project_service),
):
    return await project_service.get_all_projects()


@router.get("/{project_id}/context", response_model=ProjectContextResponse)
async def get_project_context(
    project_id: UUID,
    context_service: ProjectContextService = Depends(get_project_context_service),
):
    return await context_service.get_context(project_id)


@router.put("/{project_id}/context", response_model=ProjectContextResponse)
async def upsert_project_context(
    project_id: UUID,
    body: ProjectContextUpsert,
    context_service: ProjectContextService = Depends(get_project_context_service),
):
    return await context_service.upsert_context(project_id, body)


@router.patch("/{project_id}/context", response_model=ProjectContextResponse)
async def patch_project_context(
    project_id: UUID,
    body: ProjectContextUpdate,
    context_service: ProjectContextService = Depends(get_project_context_service),
):
    return await context_service.patch_context(project_id, body)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_by_id(
    project_id: UUID,
    project_service: ProjectService = Depends(get_project_service),
):
    return await project_service.get_project_by_id(project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project: ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service),
):
    return await project_service.update_project(project_id, project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    project_service: ProjectService = Depends(get_project_service),
):
    await project_service.delete_project(project_id)
