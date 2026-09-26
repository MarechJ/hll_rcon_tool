"""Add an optional default duration to VIP lists.

Revision ID: af731c89d215
Revises: e8c9d1a742b5
"""

import sqlalchemy as sa

from alembic import op

revision = "af731c89d215"
down_revision = "e8c9d1a742b5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "vip_list", sa.Column("default_expiration_seconds", sa.Integer(), nullable=True)
    )
    op.create_check_constraint(
        "vip_list_default_expiration_seconds_positive",
        "vip_list",
        "default_expiration_seconds > 0",
    )
    op.add_column(
        "vip_list",
        sa.Column("flags", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "player_flags",
        sa.Column(
            "managed_by_vip_list",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade():
    # List-managed flags are derived state. Preserve all manually assigned flags.
    op.execute("DELETE FROM player_flags WHERE managed_by_vip_list = true")
    op.drop_column("player_flags", "managed_by_vip_list")
    op.drop_column("vip_list", "flags")
    op.drop_constraint("vip_list_default_expiration_seconds_positive", "vip_list")
    op.drop_column("vip_list", "default_expiration_seconds")
