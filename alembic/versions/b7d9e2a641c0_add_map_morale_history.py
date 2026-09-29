"""Persist match morale history.

Revision ID: b7d9e2a641c0
Revises: 8699b1c44bfa
"""

import sqlalchemy as sa
from alembic import op

revision = "b7d9e2a641c0"
down_revision = "8699b1c44bfa"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "map_history",
        sa.Column("morale_history", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "map_history", sa.Column("initial_morale", sa.Integer(), nullable=True)
    )


def downgrade():
    op.drop_column("map_history", "initial_morale")
    op.drop_column("map_history", "morale_history")
