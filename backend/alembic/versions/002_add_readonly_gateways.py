"""Add readonly_gateways table

Revision ID: 002
Revises: 001
Create Date: 2026-05-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "readonly_gateways",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("host", sa.String(255), nullable=False),
        sa.Column("username", sa.String(128), nullable=False),
        sa.Column("password", sa.String(512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_readonly_gateways_host", "readonly_gateways", ["host"])


def downgrade() -> None:
    op.drop_index("idx_readonly_gateways_host", table_name="readonly_gateways")
    op.drop_table("readonly_gateways")
