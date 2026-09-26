"""Add VIP lists without removing legacy VIP records.

Revision ID: b7e2a91c4f10
Revises: 3f12a7b9c4d1
"""

from alembic import op
import sqlalchemy as sa


revision = "b7e2a91c4f10"
down_revision = "3f12a7b9c4d1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM player_vip
                WHERE server_number IS NULL
                   OR server_number < 1
                   OR server_number > 32
            ) THEN
                RAISE EXCEPTION
                    'player_vip contains an invalid server_number';
            END IF;
        END
        $$;
        """
    )

    op.create_table(
        "vip_list",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "sync",
            sa.Enum(
                "IGNORE_UNKNOWN",
                "REMOVE_UNKNOWN",
                name="viplistsyncmethod",
            ),
            nullable=False,
        ),
        sa.Column("servers", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "vip_list_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
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
        sa.ForeignKeyConstraint(
            ["vip_list_id"],
            ["vip_list.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "player_id_id",
            "vip_list_id",
            name="unique_vip_player_id_vip_list",
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

    op.execute(
        """
        INSERT INTO vip_list (name, sync, servers)
        SELECT
            'Migrated Server #' || server_number,
            'IGNORE_UNKNOWN',
            (1::bigint << (server_number - 1))
        FROM player_vip
        GROUP BY server_number
        ORDER BY server_number
        """
    )

    op.execute(
        """
        INSERT INTO vip_list_record (
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
            'CRCON migration',
            NOW(),
            true,
            NULL,
            NULL,
            CASE
                WHEN pv.expiration >=
                     TIMESTAMPTZ '3000-01-01 00:00:00+00'
                    THEN NULL
                ELSE pv.expiration
            END,
            pv.playersteamid_id,
            vl.id
        FROM player_vip AS pv
        JOIN vip_list AS vl
          ON vl.name = 'Migrated Server #' || pv.server_number
         AND vl.servers = (1::bigint << (pv.server_number - 1))
        """
    )


def downgrade():
    op.drop_index(
        op.f("ix_vip_list_record_vip_list_id"),
        table_name="vip_list_record",
    )
    op.drop_index(
        op.f("ix_vip_list_record_player_id_id"),
        table_name="vip_list_record",
    )
    op.drop_table("vip_list_record")
    op.drop_table("vip_list")
    op.execute("DROP TYPE IF EXISTS viplistsyncmethod")
