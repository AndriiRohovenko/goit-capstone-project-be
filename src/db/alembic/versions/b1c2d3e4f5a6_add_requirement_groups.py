"""Add requirement groups

Revision ID: b1c2d3e4f5a6
Revises: ac876de767fc
Create Date: 2026-07-21 19:52:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "ac876de767fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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

    op.add_column(
        "requirements",
        sa.Column("group_id", sa.UUID(), nullable=True),
    )

    # Backfill: one "General" group per owner who has requirements, then assign.
    op.execute(
        """
        INSERT INTO requirement_groups (id, owner_id, name, description, created_at, updated_at)
        SELECT gen_random_uuid(), p.owner_id, 'General', NULL, now(), now()
        FROM projects p
        WHERE EXISTS (
            SELECT 1 FROM requirements r WHERE r.project_id = p.id
        )
        GROUP BY p.owner_id
        """
    )
    op.execute(
        """
        UPDATE requirements r
        SET group_id = g.id
        FROM projects p
        JOIN requirement_groups g ON g.owner_id = p.owner_id AND g.name = 'General'
        WHERE r.project_id = p.id
          AND r.group_id IS NULL
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


def downgrade() -> None:
    op.drop_constraint(
        "fk_requirements_group_id_requirement_groups",
        "requirements",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_requirements_group_id"), table_name="requirements")
    op.drop_column("requirements", "group_id")
    op.drop_index(
        op.f("ix_requirement_groups_owner_id"), table_name="requirement_groups"
    )
    op.drop_table("requirement_groups")
