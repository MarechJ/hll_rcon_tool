"""blacklist overhaul

Revision ID: e246b16278c3
Revises: 22e3790f2095
Create Date: 2024-05-31 19:45:38.597865

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "e246b16278c3"
down_revision = "22e3790f2095"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "blacklist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "sync",
            sa.Enum(
                "KICK_ONLY",
                "BAN_ON_CONNECT",
                "BAN_IMMEDIATELY",
                name="blacklistsyncmethod",
            ),
            nullable=False,
        ),
        sa.Column("servers", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "blacklist_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("admin_name", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("player_id_id", sa.Integer(), nullable=False),
        sa.Column("blacklist_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["blacklist_id"], ["blacklist.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["player_id_id"],
            ["steam_id_64.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_blacklist_record_blacklist_id"),
        "blacklist_record",
        ["blacklist_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_blacklist_record_player_id_id"),
        "blacklist_record",
        ["player_id_id"],
        unique=False,
    )

    # Create default blacklist
    # Sequence starts at 1 so we use 0 as manual ID
    op.execute(
        """INSERT INTO blacklist(id, name, sync, servers)
               VALUES (0, 'Default', 'KICK_ONLY', NULL)
               ON CONFLICT DO NOTHING"""
    )
    # Migrate old blacklist records
    op.execute(
        """INSERT INTO blacklist_record(reason, admin_name, created_at, player_id_id, blacklist_id)
               SELECT COALESCE(reason, 'No ban reason provided'), COALESCE(by, 'CRCON'), NOW(), playersteamid_id, 0 FROM player_blacklist"""
    )

    ### Do not drop the old table yet - that way people can always recover their old bans if needed.
    # op.drop_table('player_blacklist')


def downgrade():
    # op.create_table('player_blacklist',
    #     sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    #     sa.Column('player_id_id', sa.INTEGER(), autoincrement=False, nullable=False),
    #     sa.Column('is_blacklisted', sa.BOOLEAN(), autoincrement=False, nullable=True),
    #     sa.Column('reason', sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.Column('by', sa.VARCHAR(), autoincrement=False, nullable=True),
    #     sa.ForeignKeyConstraint(['player_id_id'], ['player_id.id'], name='player_blacklist_player_id_id_fkey'),
    #     sa.PrimaryKeyConstraint('id', name='player_blacklist_pkey')
    # )
    op.create_index(
        "ix_player_blacklist_player_id_id",
        "player_blacklist",
        ["player_id_id"],
        unique=True,
    )
    op.drop_table("blacklist_record")
    op.drop_table("blacklist")
