"""Add level column to PlayerStats

Revision ID: 78098bd1bbb0
Revises: f80b6dc2833a
Create Date: 2025-08-12 12:37:30.321976

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78098bd1bbb0'
down_revision = 'f80b6dc2833a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('player_stats', sa.Column('level', sa.Integer, nullable=False, server_default='0'))


def downgrade():
    op.drop_column('player_stats', 'level')
