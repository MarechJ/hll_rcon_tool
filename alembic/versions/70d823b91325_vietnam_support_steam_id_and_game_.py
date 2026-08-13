"""vietnam support: steam_id and game columns

Revision ID: 70d823b91325
Revises: 29edf99df5fd
Create Date: 2026-08-13 15:00:32.272517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70d823b91325'
down_revision = '29edf99df5fd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("steam_id_64", sa.Column("steam_id", sa.String(), nullable=True))
    op.add_column("log_lines", sa.Column("game", sa.String(), nullable=False, server_default='hll'))
    op.add_column("map_history", sa.Column("game", sa.String(), nullable=False, server_default='hll'))


def downgrade():
    op.drop_column("steam_id_64", "steam_id")
    op.drop_column("log_lines", "game")
    op.drop_column("map_history", "game")
