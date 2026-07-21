from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .requirement import Requirement
    from .user import User


class RequirementGroup(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "requirement_groups"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    owner: Mapped[User] = relationship(back_populates="requirement_groups")
    requirements: Mapped[list[Requirement]] = relationship(
        back_populates="group",
    )
