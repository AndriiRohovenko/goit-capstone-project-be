"""Convert requirement groups to user-scoped

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-07-22 23:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f5a6b7c8d9e0"
down_revision: Union[str, Sequence[str], None] = "e4f5a6b7c8d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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

    # Dedupe: keep the oldest group per (owner_id, lower(name)); re-point FKs.
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                owner_id,
                lower(name) AS name_key,
                ROW_NUMBER() OVER (
                    PARTITION BY owner_id, lower(name)
                    ORDER BY created_at ASC, id ASC
                ) AS rn
            FROM requirement_groups
        ),
        keepers AS (
            SELECT id, owner_id, name_key
            FROM ranked
            WHERE rn = 1
        ),
        duplicates AS (
            SELECT r.id AS dup_id, k.id AS keep_id
            FROM ranked r
            JOIN keepers k
              ON k.owner_id = r.owner_id
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
        WITH ranked AS (
            SELECT
                id,
                owner_id,
                lower(name) AS name_key,
                ROW_NUMBER() OVER (
                    PARTITION BY owner_id, lower(name)
                    ORDER BY created_at ASC, id ASC
                ) AS rn
            FROM requirement_groups
        ),
        keepers AS (
            SELECT id, owner_id, name_key
            FROM ranked
            WHERE rn = 1
        ),
        duplicates AS (
            SELECT r.id AS dup_id, k.id AS keep_id
            FROM ranked r
            JOIN keepers k
              ON k.owner_id = r.owner_id
             AND k.name_key = r.name_key
            WHERE r.rn > 1
        )
        UPDATE coverage_reports c
        SET group_id = d.keep_id
        FROM duplicates d
        WHERE c.group_id = d.dup_id
        """
    )
    # Collapse duplicate coverage rows after remapping (same project + group).
    op.execute(
        """
        DELETE FROM coverage_reports c
        USING coverage_reports newer
        WHERE c.project_id = newer.project_id
          AND c.group_id = newer.group_id
          AND c.id <> newer.id
          AND c.updated_at < newer.updated_at
        """
    )
    op.execute(
        """
        DELETE FROM requirement_groups g
        USING (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY owner_id, lower(name)
                    ORDER BY created_at ASC, id ASC
                ) AS rn
            FROM requirement_groups
        ) ranked
        WHERE g.id = ranked.id
          AND ranked.rn > 1
        """
    )

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


def downgrade() -> None:
    op.add_column(
        "requirement_groups",
        sa.Column("project_id", sa.UUID(), nullable=True),
    )
    # Best-effort: assign to owner's most recent project.
    op.execute(
        """
        UPDATE requirement_groups g
        SET project_id = p.id
        FROM (
            SELECT DISTINCT ON (owner_id) id, owner_id
            FROM projects
            ORDER BY owner_id, created_at DESC
        ) p
        WHERE g.owner_id = p.owner_id
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
