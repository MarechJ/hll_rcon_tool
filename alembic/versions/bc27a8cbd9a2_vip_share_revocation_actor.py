"""Record the CRCON user who revokes a VIP share.

Revision ID: bc27a8cbd9a2
Revises: f91a82c407de
"""

import sqlalchemy as sa
from alembic import op

revision = "bc27a8cbd9a2"
down_revision = "f91a82c407de"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("vip_list_share", sa.Column("revoked_by", sa.String(150)))


def downgrade():
    op.drop_column("vip_list_share", "revoked_by")
