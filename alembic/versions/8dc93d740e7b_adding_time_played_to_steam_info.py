"""Adding time played to steam info

Revision ID: 8dc93d740e7b
Revises: 066d4f72edd8
Create Date: 2021-07-31 17:08:11.252179

"""
from sqlalchemy.sql.expression import null
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8dc93d740e7b'
down_revision = '066d4f72edd8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('steam_info', sa.Column('hll_game_playtime', sa.Integer, default=0, nullable=True))

def downgrade():
    pass
