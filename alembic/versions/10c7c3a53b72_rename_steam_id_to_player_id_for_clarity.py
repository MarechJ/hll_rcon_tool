"""Rename steam ID to player ID for clarity

Revision ID: 10c7c3a53b72
Revises: 22e3790f2095
Create Date: 2024-05-13 15:45:45.519114

PYTHONPATH=. alembic downgrade 22e3790f2095

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "10c7c3a53b72"
down_revision = "22e3790f2095"
branch_labels = None
depends_on = None


def upgrade():
    # Columns
    op.alter_column(
        table_name="steam_id_64", column_name="steam_id_64", new_column_name="player_id"
    )
    op.alter_column(
        table_name="player_at_count",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="player_comments",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="steam_info",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="player_watchlist",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="player_flags",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="player_optins",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="player_names",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="player_sessions",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="player_blacklist",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="players_actions",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="log_lines",
        column_name="player1_steamid",
        new_column_name="player1_player_id",
    )
    op.alter_column(
        table_name="log_lines",
        column_name="player2_steamid",
        new_column_name="player2_player_id",
    )
    op.alter_column(
        table_name="player_stats",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )
    op.alter_column(
        table_name="player_vip",
        column_name="playersteamid_id",
        new_column_name="player_id_id",
    )

    # Constraints
    op.drop_constraint("unique_player_at_count", table_name="player_at_count")
    op.create_unique_constraint(
        "unique_player_at_count",
        table_name="player_at_count",
        columns=["player_id_id", "servercount_id"],
    )

    op.drop_constraint("unique_player_server_vip", table_name="player_vip")
    op.create_unique_constraint(
        "unique_player_server_vip",
        table_name="player_vip",
        columns=["player_id_id", "server_number"],
    )

    op.drop_constraint("unique_flag_steamid", table_name="player_flags")
    op.create_unique_constraint(
        "unique_flag_player_id",
        table_name="player_flags",
        columns=["player_id_id", "flag"],
    )

    op.drop_constraint("unique_optins_steamid", table_name="player_optins")
    op.create_unique_constraint(
        "unique_optins_player_id",
        table_name="player_optins",
        columns=["player_id_id", "optin_name"],
    )

    op.drop_constraint("unique_name_steamid", table_name="player_names")
    op.create_unique_constraint(
        "unique_name_player_id",
        table_name="player_names",
        columns=["player_id_id", "name"],
    )

    op.drop_constraint("unique_map_player", table_name="player_stats")
    op.create_unique_constraint(
        "unique_map_player",
        table_name="player_stats",
        columns=["player_id_id", "map_id"],
    )

    # Tables
    op.rename_table("steam_id_64", "player_id")


def downgrade():
    # Tables
    op.rename_table("player_id", "steam_id_64")

    # Constraints
    op.drop_constraint("unique_player_at_count", table_name="player_at_count")
    op.create_unique_constraint(
        "unique_player_at_count",
        table_name="player_at_count",
        columns=["playersteamid_id", "servercount_id"],
    )

    op.drop_constraint("unique_player_server_vip", table_name="player_vip")
    op.create_unique_constraint(
        "unique_player_server_vip",
        table_name="player_vip",
        columns=["playersteamid_id", "server_number"],
    )

    op.drop_constraint("unique_flag_player_id", table_name="player_flags")
    op.create_unique_constraint(
        "unique_flag_steamid",
        table_name="player_flags",
        columns=["playersteamid_id", "flag"],
    )

    op.drop_constraint("unique_optins_player_id", table_name="player_optins")
    op.create_unique_constraint(
        "unique_optins_steamid",
        table_name="player_optins",
        columns=["playersteamid_id", "flag"],
    )

    op.drop_constraint("unique_name_player_id", table_name="player_names")
    op.create_unique_constraint(
        "unique_name_steamid",
        table_name="player_names",
        columns=["playersteamid_id", "flag"],
    )

    op.drop_constraint("unique_map_player", table_name="player_stats")
    op.create_unique_constraint(
        "unique_map_player",
        table_name="player_stats",
        columns=["playersteamid_id", "map_id"],
    )

    # Columns
    op.alter_column(
        table_name="steam_id_64", column_name="player_id", new_column_name="steam_id_64"
    )

    op.alter_column(
        table_name="player_at_count",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="player_comments",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="steam_info",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="player_watchlist",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="player_flags",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="player_optins",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="player_names",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="player_sessions",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="player_blacklist",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="players_actions",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="log_lines",
        column_name="player1_player_id",
        new_column_name="player1_steamid",
    )
    op.alter_column(
        table_name="log_lines",
        column_name="player2_player_id",
        new_column_name="player2_steamid",
    )
    op.alter_column(
        table_name="player_stats",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
    op.alter_column(
        table_name="player_vip",
        column_name="player_id_id",
        new_column_name="playersteamid_id",
    )
