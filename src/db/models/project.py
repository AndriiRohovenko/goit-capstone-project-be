from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import ProjectStatus
from .mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .requirement import Requirement
    from .user import User


class Project(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        default=ProjectStatus.ACTIVE,
        nullable=False,
    )

    owner: Mapped[User] = relationship(back_populates="projects")
    context: Mapped[ProjectContext | None] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        uselist=False,
    )
    requirements: Mapped[list[Requirement]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectContext(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_contexts"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    product_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_roles: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    business_rules: Mapped[list[str]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    authentication_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    supported_platforms: Mapped[list[str]] = mapped_column(
        JSONB, default=list, nullable=False
    )
    additional_context: Mapped[dict] = mapped_column(
        JSONB, default=dict, nullable=False
    )

    project: Mapped[Project] = relationship(back_populates="context")
