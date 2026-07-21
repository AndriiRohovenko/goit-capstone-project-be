from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.schemas.requirement_groups import (
    RequirementGroupCreate,
    RequirementGroupResponse,
    RequirementGroupUpdate,
)
from src.services.requirement_groups import (
    RequirementGroupService,
    get_requirement_group_service,
)

router = APIRouter(prefix="/requirement-groups", tags=["requirement-groups"])


@router.post(
    "",
    response_model=RequirementGroupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_requirement_group(
    body: RequirementGroupCreate,
    group_service: RequirementGroupService = Depends(get_requirement_group_service),
):
    return await group_service.create_group(body)


@router.get(
    "",
    response_model=list[RequirementGroupResponse],
)
async def get_all_requirement_groups(
    group_service: RequirementGroupService = Depends(get_requirement_group_service),
):
    return await group_service.get_all_groups()


@router.get(
    "/{group_id}",
    response_model=RequirementGroupResponse,
)
async def get_requirement_group_by_id(
    group_id: UUID,
    group_service: RequirementGroupService = Depends(get_requirement_group_service),
):
    return await group_service.get_group_by_id(group_id)


@router.put(
    "/{group_id}",
    response_model=RequirementGroupResponse,
)
async def update_requirement_group(
    group_id: UUID,
    body: RequirementGroupUpdate,
    group_service: RequirementGroupService = Depends(get_requirement_group_service),
):
    return await group_service.update_group(group_id, body)


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_requirement_group(
    group_id: UUID,
    group_service: RequirementGroupService = Depends(get_requirement_group_service),
):
    await group_service.delete_group(group_id)
