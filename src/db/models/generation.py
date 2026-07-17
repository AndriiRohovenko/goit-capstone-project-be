from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import ArtifactType, GenerationStatus, GenerationType
from .mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .requirement import Requirement


class AIGeneration(UUIDMixin, Base):
    __tablename__ = "ai_generations"

    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    generation_type: Mapped[GenerationType] = mapped_column(
        Enum(GenerationType, name="generation_type"),
        nullable=False,
    )
    status: Mapped[GenerationStatus] = mapped_column(
        Enum(GenerationStatus, name="generation_status"),
        default=GenerationStatus.PENDING,
        nullable=False,
        index=True,
    )
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str] = mapped_column(
        String(50), default="v1", nullable=False
    )
    request_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    requirement: Mapped[Requirement] = relationship(back_populates="generations")
    artifacts: Mapped[list[GeneratedArtifact]] = relationship(
        back_populates="generation",
        cascade="all, delete-orphan",
    )
    coverage_analysis: Mapped[CoverageAnalysis | None] = relationship(
        back_populates="generation",
        cascade="all, delete-orphan",
        uselist=False,
    )


class GeneratedArtifact(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "generated_artifacts"

    generation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ai_generations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    artifact_type: Mapped[ArtifactType] = mapped_column(
        Enum(ArtifactType, name="artifact_type"),
        nullable=False,
        index=True,
    )
    content: Mapped[dict | list] = mapped_column(JSONB, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    generation: Mapped[AIGeneration] = relationship(back_populates="artifacts")


class CoverageAnalysis(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "coverage_analyses"

    generation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ai_generations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    coverage_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    covered_areas: Mapped[list[dict]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    missing_areas: Mapped[list[dict]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    risks: Mapped[list[dict]] = mapped_column(JSONB, default=list, nullable=False)
    recommendations: Mapped[list[dict]] = mapped_column(
        JSONB, default=list, nullable=False
    )

    generation: Mapped[AIGeneration] = relationship(back_populates="coverage_analysis")
