from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.schemas.requirements import (
    RequirementCreate,
    RequirementResponse,
    RequirementUpdate,
)
from src.services.requirements import RequirementService, get_requirement_service

router = APIRouter(prefix="/projects", tags=["requirements"])


@router.post(
    "/{project_id}/requirements",
    response_model=RequirementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_requirement(
    project_id: UUID,
    body: RequirementCreate,
    requirement_service: RequirementService = Depends(get_requirement_service),
):
    return await requirement_service.create_requirement(project_id, body)


@router.get(
    "/{project_id}/requirements",
    response_model=list[RequirementResponse],
)
async def get_all_requirements(
    project_id: UUID,
    group_name: str | None = Query(None),
    requirement_service: RequirementService = Depends(get_requirement_service),
):
    return await requirement_service.get_all_requirements(
        project_id, group_name=group_name
    )


@router.get(
    "/{project_id}/requirements/{requirement_id}",
    response_model=RequirementResponse,
)
async def get_requirement_by_id(
    project_id: UUID,
    requirement_id: UUID,
    requirement_service: RequirementService = Depends(get_requirement_service),
):
    return await requirement_service.get_requirement_by_id(
        project_id, requirement_id
    )


@router.put(
    "/{project_id}/requirements/{requirement_id}",
    response_model=RequirementResponse,
)
async def update_requirement(
    project_id: UUID,
    requirement_id: UUID,
    body: RequirementUpdate,
    requirement_service: RequirementService = Depends(get_requirement_service),
):
    return await requirement_service.update_requirement(
        project_id, requirement_id, body
    )


@router.delete(
    "/{project_id}/requirements/{requirement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_requirement(
    project_id: UUID,
    requirement_id: UUID,
    requirement_service: RequirementService = Depends(get_requirement_service),
):
    await requirement_service.delete_requirement(project_id, requirement_id)
