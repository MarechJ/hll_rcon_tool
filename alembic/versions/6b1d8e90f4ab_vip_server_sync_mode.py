"""Move unknown-VIP synchronization policy to the gameserver.

Revision ID: 6b1d8e90f4ab
Revises: c7f42e91a6bd
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "6b1d8e90f4ab"
down_revision = "c7f42e91a6bd"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "vip_server_sync_config",
        sa.Column("server_number", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column(
            "sync",
            postgresql.ENUM(
                "IGNORE_UNKNOWN",
                "REMOVE_UNKNOWN",
                name="viplistsyncmethod",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.CheckConstraint(
            "server_number BETWEEN 1 AND 32", name="vip_server_sync_config_server_range"
        ),
    )
    # Preserve the previous effective behavior for each possible server. An
    # absent row means ignore unknown; a list with IGNORE_UNKNOWN prevents removal.
    op.execute(
        """
        INSERT INTO vip_server_sync_config (server_number, sync)
        SELECT server_number, 'REMOVE_UNKNOWN'::viplistsyncmethod
        FROM generate_series(1, 32) AS server_number
        WHERE EXISTS (
            SELECT 1 FROM vip_list
            WHERE servers IS NULL OR (servers & (1::bigint << (server_number - 1))) <> 0
        )
        AND NOT EXISTS (
            SELECT 1 FROM vip_list
            WHERE (servers IS NULL OR (servers & (1::bigint << (server_number - 1))) <> 0)
              AND sync <> 'REMOVE_UNKNOWN'::viplistsyncmethod
        )
        """
    )


def downgrade():
    # Legacy list settings remain untouched. Server policy changes made after
    # upgrade cannot be represented on lists and are discarded on downgrade.
    op.drop_table("vip_server_sync_config")
