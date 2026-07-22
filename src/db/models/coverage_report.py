from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .project import Project
    from .requirement_group import RequirementGroup


class CoverageReport(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "coverage_reports"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "group_id",
            name="uq_coverage_project_group",
        ),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("requirement_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[dict | list] = mapped_column(JSONB, nullable=False)
    coverage_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    project: Mapped[Project] = relationship()
    group: Mapped[RequirementGroup] = relationship(back_populates="coverage_reports")
