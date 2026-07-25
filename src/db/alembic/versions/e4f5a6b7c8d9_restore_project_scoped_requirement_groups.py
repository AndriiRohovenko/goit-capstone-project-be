"""Restore project-scoped requirement groups

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-07-22 23:20:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e4f5a6b7c8d9"
down_revision: Union[str, Sequence[str], None] = "d3e4f5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

requirement_group_enum = postgresql.ENUM(
    "authorization",
    "seo",
    "payments",
    "notifications",
    "general",
    name="requirement_group",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "requirement_groups",
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id", "name", name="uq_requirement_groups_project_name"
        ),
    )
    op.create_index(
        op.f("ix_requirement_groups_project_id"),
        "requirement_groups",
        ["project_id"],
        unique=False,
    )

    # Create groups from distinct enum values used on requirements.
    op.execute(
        """
        INSERT INTO requirement_groups (id, project_id, name, description, created_at, updated_at)
        SELECT
            gen_random_uuid(),
            r.project_id,
            initcap(replace(r."group"::text, '_', ' ')),
            NULL,
            now(),
            now()
        FROM requirements r
        GROUP BY r.project_id, r."group"
        """
    )
    # Also ensure groups exist for coverage rows without matching requirements.
    op.execute(
        """
        INSERT INTO requirement_groups (id, project_id, name, description, created_at, updated_at)
        SELECT
            gen_random_uuid(),
            c.project_id,
            initcap(replace(c."group"::text, '_', ' ')),
            NULL,
            now(),
            now()
        FROM coverage_reports c
        WHERE NOT EXISTS (
            SELECT 1
            FROM requirement_groups g
            WHERE g.project_id = c.project_id
              AND lower(g.name) = lower(initcap(replace(c."group"::text, '_', ' ')))
        )
        GROUP BY c.project_id, c."group"
        """
    )

    op.add_column(
        "requirements",
        sa.Column("group_id", sa.UUID(), nullable=True),
    )
    op.execute(
        """
        UPDATE requirements r
        SET group_id = g.id
        FROM requirement_groups g
        WHERE g.project_id = r.project_id
          AND lower(g.name) = lower(initcap(replace(r."group"::text, '_', ' ')))
        """
    )
    op.alter_column("requirements", "group_id", nullable=False)
    op.create_index(
        op.f("ix_requirements_group_id"),
        "requirements",
        ["group_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_requirements_group_id_requirement_groups",
        "requirements",
        "requirement_groups",
        ["group_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.drop_index(op.f("ix_requirements_group"), table_name="requirements")
    op.drop_column("requirements", "group")

    op.add_column(
        "coverage_reports",
        sa.Column("group_id", sa.UUID(), nullable=True),
    )
    op.execute(
        """
        UPDATE coverage_reports c
        SET group_id = g.id
        FROM requirement_groups g
        WHERE g.project_id = c.project_id
          AND lower(g.name) = lower(initcap(replace(c."group"::text, '_', ' ')))
        """
    )
    op.alter_column("coverage_reports", "group_id", nullable=False)
    op.drop_constraint(
        "uq_coverage_project_group",
        "coverage_reports",
        type_="unique",
    )
    op.drop_index(
        op.f("ix_coverage_reports_group"), table_name="coverage_reports"
    )
    op.drop_column("coverage_reports", "group")
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

    requirement_group_enum.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    requirement_group_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "coverage_reports",
        sa.Column("group", requirement_group_enum, nullable=True),
    )
    op.execute(
        """
        UPDATE coverage_reports c
        SET "group" = CASE lower(replace(g.name, ' ', '_'))
            WHEN 'authorization' THEN 'authorization'::requirement_group
            WHEN 'seo' THEN 'seo'::requirement_group
            WHEN 'payments' THEN 'payments'::requirement_group
            WHEN 'notifications' THEN 'notifications'::requirement_group
            ELSE 'general'::requirement_group
        END
        FROM requirement_groups g
        WHERE c.group_id = g.id
        """
    )
    op.alter_column("coverage_reports", "group", nullable=False)
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
        op.f("ix_coverage_reports_group_id"), table_name="coverage_reports"
    )
    op.drop_column("coverage_reports", "group_id")
    op.create_index(
        op.f("ix_coverage_reports_group"),
        "coverage_reports",
        ["group"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_coverage_project_group",
        "coverage_reports",
        ["project_id", "group"],
    )

    op.add_column(
        "requirements",
        sa.Column("group", requirement_group_enum, nullable=True),
    )
    op.execute(
        """
        UPDATE requirements r
        SET "group" = CASE lower(replace(g.name, ' ', '_'))
            WHEN 'authorization' THEN 'authorization'::requirement_group
            WHEN 'seo' THEN 'seo'::requirement_group
            WHEN 'payments' THEN 'payments'::requirement_group
            WHEN 'notifications' THEN 'notifications'::requirement_group
            ELSE 'general'::requirement_group
        END
        FROM requirement_groups g
        WHERE r.group_id = g.id
        """
    )
    op.alter_column("requirements", "group", nullable=False)
    op.drop_constraint(
        "fk_requirements_group_id_requirement_groups",
        "requirements",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_requirements_group_id"), table_name="requirements")
    op.drop_column("requirements", "group_id")
    op.create_index(
        op.f("ix_requirements_group"),
        "requirements",
        ["group"],
        unique=False,
    )

    op.drop_index(
        op.f("ix_requirement_groups_project_id"), table_name="requirement_groups"
    )
    op.drop_table("requirement_groups")
