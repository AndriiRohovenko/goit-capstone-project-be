from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import CoverageReport


class CoverageReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_requirement_id(
        self, requirement_id: UUID
    ) -> CoverageReport | None:
        result = await self.db.execute(
            select(CoverageReport).filter(
                CoverageReport.requirement_id == requirement_id
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        project_id: UUID,
        requirement_id: UUID,
        content: dict | list,
        *,
        coverage_score: int | None = None,
        model: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> CoverageReport:
        report = await self.get_by_requirement_id(requirement_id)
        if report is None:
            report = CoverageReport(
                project_id=project_id,
                requirement_id=requirement_id,
                content=content,
                coverage_score=coverage_score,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            self.db.add(report)
        else:
            report.content = content
            report.coverage_score = coverage_score
            report.model = model
            report.input_tokens = input_tokens
            report.output_tokens = output_tokens

        await self.db.commit()
        await self.db.refresh(report)
        return report
