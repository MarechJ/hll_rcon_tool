"""Add one default VIP list per server.

Revision ID: d4b8f3c2a1e0
Revises: b7e2a91c4f10
"""

from alembic import op
import sqlalchemy as sa


revision = "d4b8f3c2a1e0"
down_revision = "b7e2a91c4f10"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "vip_list_default",
        sa.Column(
            "server_number",
            sa.Integer(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("vip_list_id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "server_number >= 1 AND server_number <= 32",
            name="check_vip_list_default_server_number",
        ),
        sa.ForeignKeyConstraint(
            ["vip_list_id"],
            ["vip_list.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("server_number"),
    )
    op.create_index(
        op.f("ix_vip_list_default_vip_list_id"),
        "vip_list_default",
        ["vip_list_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_vip_list_default_vip_list_id"),
        table_name="vip_list_default",
    )
    op.drop_table("vip_list_default")
