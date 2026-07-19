from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import ArtifactType
from .mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .requirement import Requirement


class GeneratedArtifact(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "generated_artifacts"
    __table_args__ = (
        UniqueConstraint(
            "requirement_id",
            "artifact_type",
            name="uq_requirement_artifact_type",
        ),
    )

    requirement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("requirements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    artifact_type: Mapped[ArtifactType] = mapped_column(
        Enum(ArtifactType, name="artifact_type"),
        nullable=False,
        index=True,
    )
    content: Mapped[dict | list] = mapped_column(JSONB, nullable=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    requirement: Mapped[Requirement] = relationship(back_populates="artifacts")
