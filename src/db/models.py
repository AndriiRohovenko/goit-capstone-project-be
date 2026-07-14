from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class RequirementStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    ANALYZED = "analyzed"
    ARCHIVED = "archived"


class RequirementType(StrEnum):
    USER_STORY = "user_story"
    FEATURE = "feature"
    API = "api"
    BUSINESS_REQUIREMENT = "business_requirement"
    OTHER = "other"


class RequirementPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GenerationType(StrEnum):
    REQUIREMENT_REVIEW = "requirement_review"
    TEST_GENERATION = "test_generation"
    COVERAGE_ANALYSIS = "coverage_analysis"
    AUTOMATION_RECOMMENDATION = "automation_recommendation"


class GenerationStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ArtifactType(StrEnum):
    TEST_CASES = "test_cases"
    CHECKLIST = "checklist"
    NEGATIVE_SCENARIOS = "negative_scenarios"
    EDGE_CASES = "edge_cases"
    REQUIREMENT_REVIEW = "requirement_review"
    AUTOMATION_RECOMMENDATIONS = "automation_recommendations"


class User(UUIDMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    refresh_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )


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


class Requirement(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "requirements"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
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
    generations: Mapped[list[AIGeneration]] = relationship(
        back_populates="requirement",
        cascade="all, delete-orphan",
    )


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
