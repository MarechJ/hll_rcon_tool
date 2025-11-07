"""Add server status analytics table

Revision ID: 8220bc858c10
Revises: 0ac19ea4739e
Create Date: 2025-08-27 17:24:28.738114

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8220bc858c10'
down_revision = '0ac19ea4739e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('analytics_server_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('server_number', sa.Integer(), nullable=False),
    sa.Column('axis_count', sa.Integer(), nullable=False),
    sa.Column('allies_count', sa.Integer(), nullable=False),
    sa.Column('lobby_count', sa.Integer(), nullable=False),
    sa.Column('vip_count', sa.Integer(), nullable=False),
    sa.Column('mod_count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('analytics_server_status')
