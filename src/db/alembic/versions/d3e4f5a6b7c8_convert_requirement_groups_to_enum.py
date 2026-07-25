"""Convert requirement groups to shared enum

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-07-22 18:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, Sequence[str], None] = "c2d3e4f5a6b7"
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
    requirement_group_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "requirements",
        sa.Column("group", requirement_group_enum, nullable=True),
    )
    op.execute(
        """
        UPDATE requirements r
        SET "group" = CASE
            WHEN lower(g.name) IN (
                'authorization', 'seo', 'payments', 'notifications', 'general'
            )
                THEN lower(g.name)::requirement_group
            ELSE 'general'::requirement_group
        END
        FROM requirement_groups g
        WHERE r.group_id = g.id
        """
    )
    op.execute(
        """
        UPDATE requirements
        SET "group" = 'general'::requirement_group
        WHERE "group" IS NULL
        """
    )
    op.alter_column("requirements", "group", nullable=False)
    op.create_index(
        op.f("ix_requirements_group"),
        "requirements",
        ["group"],
        unique=False,
    )
    op.drop_constraint(
        "fk_requirements_group_id_requirement_groups",
        "requirements",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_requirements_group_id"), table_name="requirements")
    op.drop_column("requirements", "group_id")

    op.add_column(
        "coverage_reports",
        sa.Column("group", requirement_group_enum, nullable=True),
    )
    op.execute(
        """
        UPDATE coverage_reports c
        SET "group" = CASE
            WHEN lower(g.name) IN (
                'authorization', 'seo', 'payments', 'notifications', 'general'
            )
                THEN lower(g.name)::requirement_group
            ELSE 'general'::requirement_group
        END
        FROM requirement_groups g
        WHERE c.group_id = g.id
        """
    )
    op.execute(
        """
        UPDATE coverage_reports
        SET "group" = 'general'::requirement_group
        WHERE "group" IS NULL
        """
    )
    op.alter_column("coverage_reports", "group", nullable=False)
    op.drop_constraint(
        "uq_coverage_project_group",
        "coverage_reports",
        type_="unique",
    )
    op.drop_constraint(
        "coverage_reports_group_id_fkey",
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

    op.drop_index(
        op.f("ix_requirement_groups_owner_id"), table_name="requirement_groups"
    )
    op.drop_table("requirement_groups")


def downgrade() -> None:
    op.create_table(
        "requirement_groups",
        sa.Column("owner_id", sa.UUID(), nullable=False),
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
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_requirement_groups_owner_id"),
        "requirement_groups",
        ["owner_id"],
        unique=False,
    )

    # One group row per (owner, enum value) used by requirements/projects.
    op.execute(
        """
        INSERT INTO requirement_groups (id, owner_id, name, description, created_at, updated_at)
        SELECT gen_random_uuid(), p.owner_id, initcap(r."group"::text), NULL, now(), now()
        FROM requirements r
        JOIN projects p ON p.id = r.project_id
        GROUP BY p.owner_id, r."group"
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
        FROM projects p
        JOIN requirement_groups g
          ON g.owner_id = p.owner_id
         AND lower(g.name) = r."group"::text
        WHERE r.project_id = p.id
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
        FROM projects p
        JOIN requirement_groups g
          ON g.owner_id = p.owner_id
         AND lower(g.name) = c."group"::text
        WHERE c.project_id = p.id
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
        "coverage_reports_group_id_fkey",
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
