"""Add final VIP Lists schema.

Revision ID: 4f3a2c1d9e80
Revises: b7d9e2a641c0
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


revision = "4f3a2c1d9e80"
down_revision = "b7d9e2a641c0"
branch_labels = None
depends_on = None


def upgrade():
    vip_list_sync_method = postgresql.ENUM(
        "IGNORE_UNKNOWN",
        "REMOVE_UNKNOWN",
        name="viplistsyncmethod",
    )
    vip_list_sync_method.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "player_identity_game",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id_id", sa.Integer(), nullable=False),
        sa.Column("game", sa.String(length=16), nullable=False),
        sa.Column(
            "first_seen",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "last_seen",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["player_id_id"],
            ["steam_id_64.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "player_id_id",
            "game",
            name="unique_player_identity_game",
        ),
    )
    op.create_index(
        "ix_player_identity_game_player_id_id",
        "player_identity_game",
        ["player_id_id"],
        unique=False,
    )

    op.create_table(
        "vip_list",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "sync",
            postgresql.ENUM(
                "IGNORE_UNKNOWN",
                "REMOVE_UNKNOWN",
                name="viplistsyncmethod",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("servers", sa.BigInteger(), nullable=True),
        sa.Column("expired_retention_days", sa.Integer(), nullable=True),
        sa.Column("default_expiration_seconds", sa.Integer(), nullable=True),
        sa.Column(
            "flags",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
        sa.CheckConstraint(
            "expired_retention_days BETWEEN 0 AND 3650",
            name="vip_list_expired_retention_days_range",
        ),
        sa.CheckConstraint(
            "default_expiration_seconds >= 0",
            name="vip_list_default_expiration_seconds_nonnegative",
        ),
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
        sa.Column(
            "partner_approved",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "partner_excluded",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "partner_present",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "partner_deactivated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
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
        "ix_vip_list_record_player_id_id",
        "vip_list_record",
        ["player_id_id"],
        unique=False,
    )
    op.create_index(
        "ix_vip_list_record_vip_list_id",
        "vip_list_record",
        ["vip_list_id"],
        unique=False,
    )

    op.create_table(
        "vip_list_default",
        sa.Column(
            "server_number",
            sa.Integer(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("vip_list_id", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "server_number >= 1 AND server_number <= 32",
            name="check_vip_list_default_server_number",
        ),
        sa.ForeignKeyConstraint(
            ["vip_list_id"],
            ["vip_list.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("server_number"),
    )

    op.create_index(
        "ix_vip_list_default_vip_list_id",
        "vip_list_default",
        ["vip_list_id"],
        unique=False,
    )

    op.create_table(
        "vip_list_share",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "vip_list_id",
            sa.Integer(),
            sa.ForeignKey("vip_list.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_by", sa.String(150), nullable=True),
        sa.Column("last_used_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_vip_list_share_vip_list_id",
        "vip_list_share",
        ["vip_list_id"],
        unique=False,
    )

    op.create_table(
        "vip_list_import",
        sa.Column(
            "vip_list_id",
            sa.Integer(),
            sa.ForeignKey("vip_list.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("source_url", sa.String(2048), nullable=False),
        sa.Column("encrypted_token", sa.Text(), nullable=False),
        sa.Column("encrypted_webhook_url", sa.Text(), nullable=True),
        sa.Column(
            "approve_new",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column("last_success_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "last_error_notified_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column("suspended_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    op.create_table(
        "vip_server_sync_config",
        sa.Column(
            "server_number",
            sa.Integer(),
            primary_key=True,
            autoincrement=False,
        ),
        sa.Column(
            "sync",
            postgresql.ENUM(
                "IGNORE_UNKNOWN",
                "REMOVE_UNKNOWN",
                name="viplistsyncmethod",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.CheckConstraint(
            "server_number BETWEEN 1 AND 32",
            name="vip_server_sync_config_server_range",
        ),
    )

    op.create_table(
        "vip_list_pending_record",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vip_list_id", sa.Integer(), nullable=False),
        sa.Column("steam_id", sa.String(length=17), nullable=False),
        sa.Column("admin_name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "last_checked_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column("resolution_error", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["vip_list_id"],
            ["vip_list.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "steam_id",
            "vip_list_id",
            name="unique_pending_vip_steam_id_vip_list",
        ),
    )

    op.create_index(
        "ix_vip_list_pending_record_vip_list_id",
        "vip_list_pending_record",
        ["vip_list_id"],
        unique=False,
    )
    op.create_index(
        "ix_vip_list_pending_record_steam_id",
        "vip_list_pending_record",
        ["steam_id"],
        unique=False,
    )

    op.add_column(
        "player_flags",
        sa.Column(
            "managed_by_vip_list",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade():
    op.drop_column("player_flags", "managed_by_vip_list")

    op.drop_index(
        "ix_vip_list_pending_record_steam_id",
        table_name="vip_list_pending_record",
    )
    op.drop_index(
        "ix_vip_list_pending_record_vip_list_id",
        table_name="vip_list_pending_record",
    )
    op.drop_table("vip_list_pending_record")

    op.drop_table("vip_server_sync_config")
    op.drop_table("vip_list_import")

    op.drop_index(
        "ix_vip_list_share_vip_list_id",
        table_name="vip_list_share",
    )
    op.drop_table("vip_list_share")

    op.drop_index(
        "ix_vip_list_default_vip_list_id",
        table_name="vip_list_default",
    )
    op.drop_table("vip_list_default")

    op.drop_index(
        "ix_vip_list_record_vip_list_id",
        table_name="vip_list_record",
    )
    op.drop_index(
        "ix_vip_list_record_player_id_id",
        table_name="vip_list_record",
    )
    op.drop_table("vip_list_record")
    op.drop_table("vip_list")

    op.drop_index(
        "ix_player_identity_game_player_id_id",
        table_name="player_identity_game",
    )
    op.drop_table("player_identity_game")

    postgresql.ENUM(
        "IGNORE_UNKNOWN",
        "REMOVE_UNKNOWN",
        name="viplistsyncmethod",
    ).drop(op.get_bind(), checkfirst=True)
