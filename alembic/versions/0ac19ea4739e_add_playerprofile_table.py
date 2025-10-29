"""Add PlayerAccount and PlayerSoldier tables

Revision ID: 0ac19ea4739e
Revises: 78098bd1bbb0
Create Date: 2025-10-28 15:08:24.036663

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '0ac19ea4739e'
down_revision = '78098bd1bbb0'
branch_labels = None
depends_on = None


def upgrade():
    # Create the player_account table
    op.create_table(
        'player_account',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playersteamid_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('discord_id', sa.String(), nullable=True),
        sa.Column('is_member', sa.Boolean(), nullable=False, default=sa.false()),
        sa.Column('country', sa.String(2), nullable=True),
        sa.Column('lang', sa.String(2), nullable=False, default='en'),
        sa.Column('updated', sa.TIMESTAMP(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['playersteamid_id'], ['steam_id_64.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('playersteamid_id', name='unique_player_account')
    )

    # Create the player_soldier table
    op.create_table(
        'player_soldier',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playersteamid_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, default=0),
        sa.Column('platform', sa.String(), nullable=True),
        sa.Column('clan_tag', sa.String(), nullable=True),
        sa.Column('updated', sa.TIMESTAMP(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['playersteamid_id'], ['steam_id_64.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('playersteamid_id', name='unique_player_soldier')
    )
    
    # Populate the player_account & player_soldier tables with data from existing tables
    connection = op.get_bind()
    
    connection.execute(text("""
        INSERT INTO player_account (playersteamid_id, name, country, is_member, lang, updated)
        SELECT 
            p.id as playersteamid_id,
            pn.name as name,
            CASE 
                WHEN si.country = 'private' THEN NULL
                ELSE si.country
            END as country,
            false as is_member,
            'en' as lang, 
            NOW() as updated
        FROM steam_id_64 p
        LEFT JOIN LATERAL (
            SELECT name 
            FROM player_names pn 
            WHERE pn.playersteamid_id = p.id 
            ORDER BY pn.last_seen DESC 
            LIMIT 1
        ) pn ON true
        LEFT JOIN steam_info si ON si.playersteamid_id = p.id
    """))

    connection.execute(text("""
        INSERT INTO player_soldier (playersteamid_id, name, level, platform, updated)
        SELECT 
            p.id as playersteamid_id,
            pn.name as name,
            COALESCE(ps_max.level, 0) as level,
            CASE 
                WHEN LENGTH(p.steam_id_64) = 17 AND p.steam_id_64 ~ '^[0-9]+$' THEN 'steam'
                ELSE NULL
            END as platform,
            NOW() as updated
        FROM steam_id_64 p
        LEFT JOIN LATERAL (
            SELECT name 
            FROM player_names pn 
            WHERE pn.playersteamid_id = p.id 
            ORDER BY pn.last_seen DESC 
            LIMIT 1
        ) pn ON true
        LEFT JOIN LATERAL (
            SELECT MAX(level) as level
            FROM player_stats ps 
            WHERE ps.playersteamid_id = p.id 
            AND ps.level > 0
        ) ps_max ON true
    """))


def downgrade():
    # Drop the player_profile table
    op.drop_table('player_account')
    op.drop_table('player_soldier')
