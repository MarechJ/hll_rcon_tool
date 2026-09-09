"""records-players load faster

Revision ID: 8699b1c44bfa
Revises: 5cf1dd099fd3
Create Date: 2026-09-06 13:46:44.931698

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '8699b1c44bfa'
down_revision = '5cf1dd099fd3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_player_sessions_playersteamid_id_end_start_created', 'player_sessions', ['playersteamid_id', 'end', 'start', 'created'], unique=False)


def downgrade():
    op.drop_index('ix_player_sessions_playersteamid_id_end_start_created', table_name='player_sessions')
