"""Track successful reads of VIP sharing credentials.

Revision ID: d83c6a4f1b90
Revises: bc27a8cbd9a2
"""

import sqlalchemy as sa
from alembic import op

revision = "d83c6a4f1b90"
down_revision = "bc27a8cbd9a2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("vip_list_share", sa.Column("last_used_at", sa.TIMESTAMP(timezone=True)))


def downgrade():
    op.drop_column("vip_list_share", "last_used_at")
