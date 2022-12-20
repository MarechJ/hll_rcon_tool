"""Add server number to player_vip table (PlayerVIP)

Revision ID: 8d313a5e52b7
Revises: 23fd01b846e8
Create Date: 2022-12-10 13:10:16.318869

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d313a5e52b7'
down_revision = '23fd01b846e8'
branch_labels = None
depends_on = None


def upgrade():
    # add server number
    op.add_column("player_vip", sa.Column("server_number", sa.Integer(), nullable=True))
    op.create_unique_constraint("unique_player_server_vip", "player_vip", ["playersteamid_id", "server_number"])


def downgrade():
    op.drop_column("player_comments", "by")
    op.drop_constraint("unique_player_server_vip", "player_vip", type_="unique")
