"""VIP list overhaul

Revision ID: c8b8a0bf2c8f
Revises: f8c2fb0a8b8c
Create Date: 2025-02-05 03:03:23.902509

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c8b8a0bf2c8f"
down_revision = "f8c2fb0a8b8c"
branch_labels = None
depends_on = None


def upgrade():
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
    pass
