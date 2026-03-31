"""vip rework to vip lists

Revision ID: dc4df9b41ca4
Revises: 89a3502370a0
Create Date: 2026-03-31 08:53:14.047059

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc4df9b41ca4'
down_revision = '89a3502370a0'
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "vip_list",
        sa.Column("id", sa.Integer, nullable=False, primary_key=True),
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
        sa.UniqueConstraint(
            "id", "player_id_id", "vip_list_id", name="unique_vip_player_id_vip_list"
        ),
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
        """INSERT INTO vip_list(name, sync, servers)
               VALUES ('Seed VIP', 'IGNORE_UNKNOWN', NULL)
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
                CASE WHEN expiration > '2030-01-01' THEN NULL ELSE expiration END,
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
                    WHERE server_number IS NOT NULL
                ) sub
            WHERE
                sub.rn = 1
            """
    )

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
    op.drop_table("vip_list_record")
    op.drop_table("vip_list")
    op.execute("DROP TYPE viplistsyncmethod")
