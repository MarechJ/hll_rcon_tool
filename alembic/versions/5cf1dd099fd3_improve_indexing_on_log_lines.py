"""Improve indexing on log_lines

Revision ID: 5cf1dd099fd3
Revises: 3f12a7b9c4d1
Create Date: 2026-08-24 18:00:16.458454

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '5cf1dd099fd3'
down_revision = '3f12a7b9c4d1'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.drop_index(op.f('ix_log_lines_player1_steamid'), table_name='log_lines')
    op.drop_index(op.f('ix_log_lines_player2_steamid'), table_name='log_lines')
    op.create_index('ix_log_lines_player1_name_event_time', 'log_lines', ['player1_name', 'event_time'], unique=False)
    op.create_index('ix_log_lines_player1_name_trgm', 'log_lines', ['player1_name'], unique=False, postgresql_using='gin', postgresql_ops={'player1_name': 'gin_trgm_ops'})
    op.create_index('ix_log_lines_player1_steamid_event_time', 'log_lines', ['player1_steamid', 'event_time'], unique=False)
    op.create_index('ix_log_lines_player2_name_event_time', 'log_lines', ['player2_name', 'event_time'], unique=False)
    op.create_index('ix_log_lines_player2_name_trgm', 'log_lines', ['player2_name'], unique=False, postgresql_using='gin', postgresql_ops={'player2_name': 'gin_trgm_ops'})
    op.create_index('ix_log_lines_player2_steamid_event_time', 'log_lines', ['player2_steamid', 'event_time'], unique=False)
    op.create_index('ix_log_lines_server_event_time_id', 'log_lines', ['server', 'event_time', 'id'], unique=False)
    op.create_index('ix_log_lines_type_event_time', 'log_lines', ['type', 'event_time'], unique=False)
    op.create_index('ix_log_lines_type_trgm', 'log_lines', ['type'], unique=False, postgresql_using='gin', postgresql_ops={'type': 'gin_trgm_ops'})


def downgrade():
    op.drop_index('ix_log_lines_type_trgm', table_name='log_lines', postgresql_using='gin', postgresql_ops={'type': 'gin_trgm_ops'})
    op.drop_index('ix_log_lines_type_event_time', table_name='log_lines')
    op.drop_index('ix_log_lines_server_event_time_id', table_name='log_lines')
    op.drop_index('ix_log_lines_player2_steamid_event_time', table_name='log_lines')
    op.drop_index('ix_log_lines_player2_name_trgm', table_name='log_lines', postgresql_using='gin', postgresql_ops={'player2_name': 'gin_trgm_ops'})
    op.drop_index('ix_log_lines_player2_name_event_time', table_name='log_lines')
    op.drop_index('ix_log_lines_player1_steamid_event_time', table_name='log_lines')
    op.drop_index('ix_log_lines_player1_name_trgm', table_name='log_lines', postgresql_using='gin', postgresql_ops={'player1_name': 'gin_trgm_ops'})
    op.drop_index('ix_log_lines_player1_name_event_time', table_name='log_lines')
    op.create_index(op.f('ix_log_lines_player2_steamid'), 'log_lines', ['player2_steamid'], unique=False)
    op.create_index(op.f('ix_log_lines_player1_steamid'), 'log_lines', ['player1_steamid'], unique=False)
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
