"""Add ldap_configs table

Revision ID: 003
Revises: 002
Create Date: 2026-05-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ldap_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("host", sa.String(255), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False, server_default=sa.text("389")),
        sa.Column("base_dn", sa.String(512), nullable=False),
        sa.Column("bind_dn", sa.String(512), nullable=False),
        sa.Column("bind_password", sa.String(512), nullable=False),
        sa.Column("use_tls", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ldap_configs_host", "ldap_configs", ["host"])


def downgrade() -> None:
    op.drop_index("idx_ldap_configs_host", table_name="ldap_configs")
    op.drop_table("ldap_configs")
