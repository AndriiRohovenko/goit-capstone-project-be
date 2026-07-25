"""Convert groups to project-scoped and coverage to per-requirement

Revision ID: a1b2c3d4e5f6
Revises: f5a6b7c8d9e0
Create Date: 2026-07-25 22:40:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f5a6b7c8d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- coverage_reports: drop old group-based reports (semantics change) ---
    op.execute("DELETE FROM coverage_reports")

    op.drop_constraint(
        "uq_coverage_project_group",
        "coverage_reports",
        type_="unique",
    )
    op.drop_constraint(
        "fk_coverage_reports_group_id_requirement_groups",
        "coverage_reports",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_coverage_reports_group_id"),
        table_name="coverage_reports",
    )
    op.drop_column("coverage_reports", "group_id")

    op.add_column(
        "coverage_reports",
        sa.Column("requirement_id", sa.UUID(), nullable=False),
    )
    op.create_index(
        op.f("ix_coverage_reports_requirement_id"),
        "coverage_reports",
        ["requirement_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_coverage_reports_requirement_id_requirements",
        "coverage_reports",
        "requirements",
        ["requirement_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_coverage_requirement",
        "coverage_reports",
        ["requirement_id"],
    )

    # --- requirement_groups: owner-scoped -> project-scoped ---
    op.add_column(
        "requirement_groups",
        sa.Column("project_id", sa.UUID(), nullable=True),
    )

    # Build mapping of distinct (old_group_id, project_id) usages.
    # Keep original group for the lexicographically first project_id;
    # clone for every additional project.
    op.execute(
        """
        CREATE TEMP TABLE group_usage AS
        SELECT
            r.group_id AS old_group_id,
            r.project_id,
            ROW_NUMBER() OVER (
                PARTITION BY r.group_id ORDER BY r.project_id
            ) AS rn
        FROM (
            SELECT DISTINCT group_id, project_id
            FROM requirements
        ) r
        """
    )

    op.execute(
        """
        UPDATE requirement_groups g
        SET project_id = u.project_id
        FROM group_usage u
        WHERE g.id = u.old_group_id
          AND u.rn = 1
        """
    )

    op.execute(
        """
        CREATE TEMP TABLE cloned_groups AS
        SELECT
            gen_random_uuid() AS new_group_id,
            u.old_group_id,
            u.project_id,
            g.name,
            g.description,
            g.created_at,
            g.updated_at,
            g.owner_id
        FROM group_usage u
        JOIN requirement_groups g ON g.id = u.old_group_id
        WHERE u.rn > 1
        """
    )

    op.execute(
        """
        INSERT INTO requirement_groups (
            id, project_id, name, description, created_at, updated_at, owner_id
        )
        SELECT
            new_group_id,
            project_id,
            name,
            description,
            created_at,
            updated_at,
            owner_id
        FROM cloned_groups
        """
    )

    op.execute(
        """
        UPDATE requirements r
        SET group_id = c.new_group_id
        FROM cloned_groups c
        WHERE r.group_id = c.old_group_id
          AND r.project_id = c.project_id
        """
    )

    # Orphan groups (no requirements): attach to owner's earliest project
    op.execute(
        """
        UPDATE requirement_groups g
        SET project_id = p.id
        FROM (
            SELECT DISTINCT ON (owner_id) id, owner_id
            FROM projects
            ORDER BY owner_id, created_at ASC
        ) p
        WHERE g.project_id IS NULL
          AND g.owner_id = p.owner_id
        """
    )
    op.execute("DELETE FROM requirement_groups WHERE project_id IS NULL")

    # Collapse duplicate names within a project
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                project_id,
                lower(name) AS name_key,
                ROW_NUMBER() OVER (
                    PARTITION BY project_id, lower(name)
                    ORDER BY created_at ASC, id ASC
                ) AS rn
            FROM requirement_groups
        ),
        keepers AS (
            SELECT id, project_id, name_key FROM ranked WHERE rn = 1
        ),
        duplicates AS (
            SELECT r.id AS dup_id, k.id AS keep_id
            FROM ranked r
            JOIN keepers k
              ON k.project_id = r.project_id
             AND k.name_key = r.name_key
            WHERE r.rn > 1
        )
        UPDATE requirements req
        SET group_id = d.keep_id
        FROM duplicates d
        WHERE req.group_id = d.dup_id
        """
    )
    op.execute(
        """
        DELETE FROM requirement_groups g
        USING (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY project_id, lower(name)
                    ORDER BY created_at ASC, id ASC
                ) AS rn
            FROM requirement_groups
        ) ranked
        WHERE g.id = ranked.id
          AND ranked.rn > 1
        """
    )

    op.alter_column("requirement_groups", "project_id", nullable=False)

    op.drop_constraint(
        "uq_requirement_groups_owner_name",
        "requirement_groups",
        type_="unique",
    )
    op.drop_constraint(
        "fk_requirement_groups_owner_id_users",
        "requirement_groups",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_requirement_groups_owner_id"),
        table_name="requirement_groups",
    )
    op.drop_column("requirement_groups", "owner_id")

    op.create_index(
        op.f("ix_requirement_groups_project_id"),
        "requirement_groups",
        ["project_id"],
        unique=False,
    )
    op.create_foreign_key(
        "requirement_groups_project_id_fkey",
        "requirement_groups",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_requirement_groups_project_name",
        "requirement_groups",
        ["project_id", "name"],
    )

    op.execute("DROP TABLE IF EXISTS cloned_groups")
    op.execute("DROP TABLE IF EXISTS group_usage")


def downgrade() -> None:
    op.add_column(
        "requirement_groups",
        sa.Column("owner_id", sa.UUID(), nullable=True),
    )
    op.execute(
        """
        UPDATE requirement_groups g
        SET owner_id = p.owner_id
        FROM projects p
        WHERE g.project_id = p.id
        """
    )
    op.alter_column("requirement_groups", "owner_id", nullable=False)

    op.drop_constraint(
        "uq_requirement_groups_project_name",
        "requirement_groups",
        type_="unique",
    )
    op.drop_constraint(
        "requirement_groups_project_id_fkey",
        "requirement_groups",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_requirement_groups_project_id"),
        table_name="requirement_groups",
    )
    op.drop_column("requirement_groups", "project_id")

    op.create_index(
        op.f("ix_requirement_groups_owner_id"),
        "requirement_groups",
        ["owner_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_requirement_groups_owner_id_users",
        "requirement_groups",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_requirement_groups_owner_name",
        "requirement_groups",
        ["owner_id", "name"],
    )

    op.execute("DELETE FROM coverage_reports")
    op.drop_constraint(
        "uq_coverage_requirement",
        "coverage_reports",
        type_="unique",
    )
    op.drop_constraint(
        "fk_coverage_reports_requirement_id_requirements",
        "coverage_reports",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_coverage_reports_requirement_id"),
        table_name="coverage_reports",
    )
    op.drop_column("coverage_reports", "requirement_id")

    op.add_column(
        "coverage_reports",
        sa.Column("group_id", sa.UUID(), nullable=False),
    )
    op.create_index(
        op.f("ix_coverage_reports_group_id"),
        "coverage_reports",
        ["group_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_coverage_reports_group_id_requirement_groups",
        "coverage_reports",
        "requirement_groups",
        ["group_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_coverage_project_group",
        "coverage_reports",
        ["project_id", "group_id"],
    )
