"""create player_vip table

Revision ID: e87989f4783a
Revises: 066d4f72edd8
Create Date: 2022-10-14 10:12:41.922719

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e87989f4783a"
down_revision = "066d4f72edd8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "player_vip",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("expiration", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("playersteamid_id", sa.Integer, sa.ForeignKey("steam_id_64.id")),
    )


def downgrade():
    op.drop_table("player_vip")
