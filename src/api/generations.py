from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.schemas.generations import GenerationCreate, GenerationResponse
from src.services.generations import GenerationService, get_generation_service

router = APIRouter(prefix="/projects", tags=["generations"])


@router.post(
    "/{project_id}/requirements/{requirement_id}/generations",
    response_model=GenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_generation(
    project_id: UUID,
    requirement_id: UUID,
    body: GenerationCreate,
    generation_service: GenerationService = Depends(get_generation_service),
):
    return await generation_service.create_generation(
        project_id, requirement_id, body
    )


@router.get(
    "/{project_id}/requirements/{requirement_id}/generations",
    response_model=list[GenerationResponse],
)
async def get_all_generations(
    project_id: UUID,
    requirement_id: UUID,
    generation_service: GenerationService = Depends(get_generation_service),
):
    return await generation_service.get_all_generations(project_id, requirement_id)


@router.get(
    "/{project_id}/requirements/{requirement_id}/generations/{generation_id}",
    response_model=GenerationResponse,
)
async def get_generation_by_id(
    project_id: UUID,
    requirement_id: UUID,
    generation_id: UUID,
    generation_service: GenerationService = Depends(get_generation_service),
):
    return await generation_service.get_generation_by_id(
        project_id, requirement_id, generation_id
    )
