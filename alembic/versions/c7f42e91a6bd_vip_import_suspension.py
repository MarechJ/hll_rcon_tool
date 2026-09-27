"""Track partner-feed outages independently of partner removals.

Revision ID: c7f42e91a6bd
Revises: d83c6a4f1b90
"""

import sqlalchemy as sa
from alembic import op

revision = "c7f42e91a6bd"
down_revision = "d83c6a4f1b90"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("vip_list_import", sa.Column("suspended_at", sa.TIMESTAMP(timezone=True)))


def downgrade():
    op.drop_column("vip_list_import", "suspended_at")
