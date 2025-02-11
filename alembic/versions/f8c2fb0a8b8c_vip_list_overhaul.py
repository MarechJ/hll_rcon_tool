"""VIP list overhaul

Revision ID: f8c2fb0a8b8c
Revises: 1e8fd0c19cb0
Create Date: 2025-02-05 03:03:23.902509

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f8c2fb0a8b8c"
down_revision = "1e8fd0c19cb0"
branch_labels = None
depends_on = None


def upgrade():
    # add email and discord ID columns to PlayerID
    op.add_column("steam_id_64", sa.Column("email", sa.String(), nullable=True))
    op.add_column("steam_id_64", sa.Column("discord_id", sa.String(), nullable=True))

    op.create_table(
        "vip_list",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "sync",
            sa.Enum("IGNORE_UNKNOWN", "REMOVE_UNKNOWN", name="viplistsyncmethod"),
            nullable=False,
        ),
        sa.Column("servers", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "vip_list_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_name", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("player_id_id", sa.Integer(), nullable=False),
        sa.Column("vip_list_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["player_id_id"],
            ["steam_id_64.id"],
        ),
        sa.ForeignKeyConstraint(["vip_list_id"], ["vip_list.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_vip_list_record_player_id_id"),
        "vip_list_record",
        ["player_id_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_vip_list_record_vip_list_id"),
        "vip_list_record",
        ["vip_list_id"],
        unique=False,
    )

    # Create default vip list from player_vip table
    # using ID 0 for the default list
    # and ID 1 for the default Seed VIP list
    # We can't prefill the Seed VIP list reliably because it requires a game
    # server connection and this runs in the maintenance container; but future
    # records by default will go to the Seed VIP list
    op.execute(
        """INSERT INTO vip_list(id, name, sync, servers)
               VALUES (0, 'Default', 'IGNORE_UNKNOWN', NULL)
               ON CONFLICT DO NOTHING"""
    )
    op.execute(
        """INSERT INTO vip_list(id, name, sync, servers)
               VALUES (1, 'Seed VIP', 'IGNORE_UNKNOWN', NULL)
               ON CONFLICT DO NOTHING"""
    )
    # Migrate old VIP records; this is not the same as VIP entries on the game server
    # but whatever records were in player_vip
    # We can't access their description; that is stored on the game server
    # and this is run in the maintenance container with no connection to any server
    op.execute(
        """INSERT INTO
            vip_list_record (
                admin_name,
                created_at,
                active,
                description,
                notes,
                expires_at,
                player_id_id,
                vip_list_id
            )
            SELECT
                'CRCON',
                NOW (),
                true,
                NULL,
                NULL,
                COALESCE(expiration, NULL),
                playersteamid_id,
                0
            FROM
                (
                    SELECT
                        expiration,
                        playersteamid_id,
                        ROW_NUMBER() OVER (
                            PARTITION BY
                                playersteamid_id
                            ORDER BY
                                expiration DESC
                        ) AS rn
                    FROM
                        player_vip
                ) sub
            WHERE
                sub.rn = 1
            LIMIT
                10;"""
    )

    op.drop_table("player_vip")
    op.drop_constraint("unique_player_server_vip", "player_vip", type_="unique")
    op.drop_index(op.f("ix_player_vip_playersteamid_id"), table_name="player_vip")
    op.drop_table("player_vip")


def downgrade():
    op.create_table(
        "player_vip",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("expiration", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "playersteamid_id",
            sa.Integer,
            sa.ForeignKey("steam_id_64.id"),
            nullable=False,
        ),
        sa.Column("server_number", sa.Integer(), nullable=True),
    )

    op.create_unique_constraint(
        "unique_player_server_vip", "player_vip", ["playersteamid_id", "server_number"]
    )
    op.create_index(
        op.f("ix_player_vip_playersteamid_id"),
        "player_vip",
        ["playersteamid_id"],
        unique=False,
    )
    op.drop_column("steam_id_64", "email")
    op.drop_column("steam_id_64", "discord_id")
    op.drop_table("vip_list_record")
    op.drop_table("vip_list")
    op.execute("DROP TYPE viplistsyncmethod")
