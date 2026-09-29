"""Add individual read-only sharing credentials for VIP lists.

Revision ID: f91a82c407de
Revises: c4e9a6b183d2
"""

import sqlalchemy as sa
from alembic import op

revision = "f91a82c407de"
down_revision = "c4e9a6b183d2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "vip_list_share",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vip_list_id", sa.Integer(), sa.ForeignKey("vip_list.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True)),
    )
    op.create_index("ix_vip_list_share_vip_list_id", "vip_list_share", ["vip_list_id"])
    op.create_table(
        "vip_list_import",
        sa.Column("vip_list_id", sa.Integer(), sa.ForeignKey("vip_list.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("source_url", sa.String(2048), nullable=False),
        sa.Column("encrypted_token", sa.Text(), nullable=False),
        sa.Column("encrypted_webhook_url", sa.Text()),
        sa.Column("approve_new", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_success_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("last_error_notified_at", sa.TIMESTAMP(timezone=True)),
    )
    op.add_column("vip_list_record", sa.Column("partner_approved", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("vip_list_record", sa.Column("partner_excluded", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("vip_list_record", sa.Column("partner_present", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("vip_list_record", sa.Column("partner_deactivated_at", sa.TIMESTAMP(timezone=True)))


def downgrade():
    op.drop_column("vip_list_record", "partner_deactivated_at")
    op.drop_column("vip_list_record", "partner_present")
    op.drop_column("vip_list_record", "partner_excluded")
    op.drop_column("vip_list_record", "partner_approved")
    op.drop_table("vip_list_import")
    op.drop_index("ix_vip_list_share_vip_list_id", table_name="vip_list_share")
    op.drop_table("vip_list_share")
