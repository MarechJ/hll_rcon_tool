"""Add optional retention policy for expired VIP list records.

Revision ID: e8c9d1a742b5
Revises: c6f4a1d82e39
"""

import sqlalchemy as sa
from alembic import op

revision = "e8c9d1a742b5"
down_revision = "c6f4a1d82e39"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "vip_list",
        sa.Column("expired_retention_days", sa.Integer(), nullable=True),
    )
    op.create_check_constraint(
        "vip_list_expired_retention_days_range",
        "vip_list",
        "expired_retention_days BETWEEN 0 AND 3650",
    )


def downgrade():
    op.drop_constraint("vip_list_expired_retention_days_range", "vip_list")
    op.drop_column("vip_list", "expired_retention_days")
