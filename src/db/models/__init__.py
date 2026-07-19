"""SQLAlchemy models package.

Importing this package registers all models on ``Base.metadata`` so Alembic
autogenerate and ``from src.db.models import …`` keep working without a
flat ``models.py`` file.
"""

from .artifact import GeneratedArtifact
from .base import Base
from .enums import (
    ArtifactType,
    GenerationType,
    ProjectStatus,
    RequirementPriority,
    RequirementStatus,
    RequirementType,
)
from .mixins import TimestampMixin, UUIDMixin
from .project import Project, ProjectContext
from .requirement import Requirement
from .user import User

__all__ = [
    "ArtifactType",
    "Base",
    "GeneratedArtifact",
    "GenerationType",
    "Project",
    "ProjectContext",
    "ProjectStatus",
    "Requirement",
    "RequirementPriority",
    "RequirementStatus",
    "RequirementType",
    "TimestampMixin",
    "User",
    "UUIDMixin",
]
