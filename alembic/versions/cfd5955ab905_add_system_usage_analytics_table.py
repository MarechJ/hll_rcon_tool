"""Add system usage analytics table

Revision ID: cfd5955ab905
Revises: 8220bc858c10
Create Date: 2025-08-28 14:28:41.841267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfd5955ab905'
down_revision = '8220bc858c10'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('analytics_system_usage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('cpu_cores', sa.Integer(), nullable=False),
    sa.Column('cpu_percent', sa.Float(), nullable=False),
    sa.Column('cpu_process_count', sa.Integer(), nullable=False),
    sa.Column('ram_total', sa.Float(), nullable=False),
    sa.Column('ram_used', sa.Float(), nullable=False),
    sa.Column('ram_percent', sa.Float(), nullable=False),
    sa.Column('disk_total', sa.Float(), nullable=False),
    sa.Column('disk_used', sa.Float(), nullable=False),
    sa.Column('disk_percent', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('analytics_system_usage')
