from enum import StrEnum


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


class ArtifactType(StrEnum):
    TEST_CASES = "test_cases"
    CHECKLIST = "checklist"
    NEGATIVE_SCENARIOS = "negative_scenarios"
    EDGE_CASES = "edge_cases"
    REQUIREMENT_REVIEW = "requirement_review"
    AUTOMATION_RECOMMENDATIONS = "automation_recommendations"
