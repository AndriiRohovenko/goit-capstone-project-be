from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.db.models.enums import ArtifactType
from src.schemas.artifacts import (
    ArtifactGenerateRequest,
    ArtifactResponse,
    ArtifactUpdateRequest,
)
from src.services.artifacts import ArtifactService, get_artifact_service

router = APIRouter(prefix="/projects", tags=["artifacts"])


@router.post(
    "/{project_id}/requirements/{requirement_id}/artifacts/generate",
    response_model=list[ArtifactResponse],
    status_code=status.HTTP_200_OK,
)
async def generate_artifacts(
    project_id: UUID,
    requirement_id: UUID,
    body: ArtifactGenerateRequest,
    artifact_service: ArtifactService = Depends(get_artifact_service),
):
    return await artifact_service.generate(project_id, requirement_id, body)


@router.get(
    "/{project_id}/requirements/{requirement_id}/artifacts",
    response_model=list[ArtifactResponse],
)
async def get_all_artifacts(
    project_id: UUID,
    requirement_id: UUID,
    artifact_service: ArtifactService = Depends(get_artifact_service),
):
    return await artifact_service.get_all_artifacts(project_id, requirement_id)


@router.get(
    "/{project_id}/requirements/{requirement_id}/artifacts/{artifact_type}",
    response_model=ArtifactResponse,
)
async def get_artifact_by_type(
    project_id: UUID,
    requirement_id: UUID,
    artifact_type: ArtifactType,
    artifact_service: ArtifactService = Depends(get_artifact_service),
):
    return await artifact_service.get_artifact_by_type(
        project_id, requirement_id, artifact_type
    )


@router.patch(
    "/{project_id}/requirements/{requirement_id}/artifacts/{artifact_type}",
    response_model=ArtifactResponse,
)
async def update_artifact(
    project_id: UUID,
    requirement_id: UUID,
    artifact_type: ArtifactType,
    body: ArtifactUpdateRequest,
    artifact_service: ArtifactService = Depends(get_artifact_service),
):
    return await artifact_service.update_artifact(
        project_id, requirement_id, artifact_type, body
    )


@router.post(
    "/{project_id}/requirements/{requirement_id}/artifacts/{artifact_type}/regenerate",
    response_model=ArtifactResponse,
)
async def regenerate_artifact(
    project_id: UUID,
    requirement_id: UUID,
    artifact_type: ArtifactType,
    artifact_service: ArtifactService = Depends(get_artifact_service),
):
    return await artifact_service.regenerate(
        project_id, requirement_id, artifact_type
    )
