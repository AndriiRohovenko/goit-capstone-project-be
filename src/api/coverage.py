from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.schemas.coverage import CoverageReportResponse
from src.services.coverage import CoverageService, get_coverage_service

router = APIRouter(prefix="/projects", tags=["coverage"])


@router.post(
    "/{project_id}/coverage/{group_id}",
    response_model=CoverageReportResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_group_coverage(
    project_id: UUID,
    group_id: UUID,
    coverage_service: CoverageService = Depends(get_coverage_service),
):
    return await coverage_service.analyze(project_id, group_id)


@router.post(
    "/{project_id}/coverage",
    response_model=list[CoverageReportResponse],
    status_code=status.HTTP_200_OK,
)
async def analyze_all_coverage(
    project_id: UUID,
    coverage_service: CoverageService = Depends(get_coverage_service),
):
    return await coverage_service.analyze_all(project_id)


@router.get(
    "/{project_id}/coverage/{group_id}",
    response_model=CoverageReportResponse,
)
async def get_group_coverage(
    project_id: UUID,
    group_id: UUID,
    coverage_service: CoverageService = Depends(get_coverage_service),
):
    return await coverage_service.get_report(project_id, group_id)
