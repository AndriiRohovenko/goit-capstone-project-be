from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import RequirementPriority, RequirementStatus, RequirementType
from .mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .artifact import GeneratedArtifact
    from .project import Project
    from .requirement_group import RequirementGroup


class Requirement(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "requirements"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("requirement_groups.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    acceptance_criteria: Mapped[list[str]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    business_rules: Mapped[list[str]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    requirement_type: Mapped[RequirementType] = mapped_column(
        Enum(RequirementType, name="requirement_type"),
        default=RequirementType.USER_STORY,
        nullable=False,
    )
    priority: Mapped[RequirementPriority] = mapped_column(
        Enum(RequirementPriority, name="requirement_priority"),
        default=RequirementPriority.MEDIUM,
        nullable=False,
    )
    status: Mapped[RequirementStatus] = mapped_column(
        Enum(RequirementStatus, name="requirement_status"),
        default=RequirementStatus.DRAFT,
        nullable=False,
    )
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )

    project: Mapped[Project] = relationship(back_populates="requirements")
    group: Mapped[RequirementGroup] = relationship(back_populates="requirements")
    artifacts: Mapped[list[GeneratedArtifact]] = relationship(
        back_populates="requirement",
        cascade="all, delete-orphan",
    )
