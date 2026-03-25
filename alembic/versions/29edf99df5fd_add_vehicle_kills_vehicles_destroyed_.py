"""add vehicle_kills, vehicles_destroyed, kills_and_assists, deaths_and_redeploys, units, cap_flips and match_time columns

Revision ID: 29edf99df5fd
Revises: 89a3502370a0
Create Date: 2026-03-13 13:49:09.208794

"""
from alembic import op
import sqlalchemy as sa

revision = '29edf99df5fd'
down_revision = '89a3502370a0'
branch_labels = None
depends_on = None


def upgrade():
    # Integer columns (same style as the original migration)
    op.add_column(
        'player_stats',
        sa.Column('vehicle_kills', sa.Integer, nullable=False, server_default='0')
    )
    op.add_column(
        'player_stats',
        sa.Column('vehicles_destroyed', sa.Integer, nullable=False, server_default='0')
    )
    op.add_column(
        'player_stats',
        sa.Column('kills_and_assists', sa.Integer, nullable=False, server_default='0')
    )
    op.add_column(
        'player_stats',
        sa.Column('deaths_and_redeploys', sa.Integer, nullable=False, server_default='0')
    )

    # JSON column for unit history: list of { "ts": int, "t": int, "s": int, "r": int }
    op.add_column(
        'player_stats',
        sa.Column('units', sa.JSON, nullable=False, server_default='[]')
    )

    op.add_column(
        'map_history',
        sa.Column('cap_flips', sa.JSON, nullable=False, server_default='[]')
    )

    op.add_column(
        'map_history',
        sa.Column('match_time', sa.Integer, nullable=False, server_default='0')
    )


def downgrade():
    op.drop_column('map_history', 'match_time')
    op.drop_column('map_history', 'cap_flips')
    op.drop_column('player_stats', 'units')
    op.drop_column('player_stats', 'deaths_and_redeploys')
    op.drop_column('player_stats', 'kills_and_assists')
    op.drop_column('player_stats', 'vehicles_destroyed')
    op.drop_column('player_stats', 'vehicle_kills')