"""Split user_config key into game, server number, and name.

Revision ID: 3f12a7b9c4d1
Revises: 70d823b91325
Create Date: 2026-08-17

"""

import os

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3f12a7b9c4d1"
down_revision = "70d823b91325"
branch_labels = None
depends_on = None


UNIQUE_CONSTRAINT = "uq_user_config_game_server_number_name"
MAX_SERVER_CONFIGURATIONS = 100
GAME_IDS = {
    "hll": 1,
    "hllv": 2,
}


def _configured_server_games(environ=None):
    environ = os.environ if environ is None else environ
    server_games = {}

    for index in range(1, MAX_SERVER_CONFIGURATIONS + 1):
        suffix = "" if index == 1 else f"_{index}"
        server_key = f"SERVER_NUMBER{suffix}"
        game_key = f"HLL_GAME{suffix}"
        raw_server_number = environ.get(server_key)
        raw_game = environ.get(game_key)

        if not raw_server_number:
            if raw_game:
                raise RuntimeError(f"{game_key} is set but {server_key} is missing")
            continue

        try:
            server_number = int(raw_server_number)
        except ValueError as error:
            raise RuntimeError(
                f"{server_key} must be an integer, got {raw_server_number!r}"
            ) from error

        if server_number < 1:
            raise RuntimeError(
                f"{server_key} must be greater than zero, got {server_number}"
            )

        # This mirrors `${HLL_GAME_N:-hll}` in the Compose services.
        game = raw_game or "hll"
        try:
            game_id = GAME_IDS[game]
        except KeyError as error:
            raise RuntimeError(
                f"{game_key} must be one of {sorted(GAME_IDS)}, got {game!r}"
            ) from error

        existing_game_id = server_games.get(server_number)
        if existing_game_id is not None and existing_game_id != game_id:
            raise RuntimeError(
                f"Server number {server_number} is configured for multiple games"
            )
        server_games[server_number] = game_id

    if not server_games:
        raise RuntimeError("No server/game configuration was provided")

    return server_games


def upgrade():
    server_games = _configured_server_games()

    op.add_column(
        "user_config",
        sa.Column("server_number", sa.Integer(), nullable=True),
    )
    op.add_column(
        "user_config",
        sa.Column(
            "game",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.add_column(
        "user_config",
        sa.Column("name", sa.String(), nullable=True),
    )

    # This table historically accepted arbitrary JSON, so not every row is a
    # user config. Discard rows that cannot be represented by the new schema
    # before attempting to cast the server-number prefix.
    op.execute(
        """
        DELETE FROM user_config
        WHERE key IS NULL OR key !~ '^[0-9]+_.+$'
        """
    )

    # Valid-looking configs may belong to servers that have since been removed
    # from the installation. Numeric avoids overflowing on an unusually large
    # digit-only prefix; all retained values are configured integer IDs.
    configured_server_numbers = ", ".join(
        str(server_number) for server_number in sorted(server_games)
    )
    op.execute(
        f"""
        DELETE FROM user_config
        WHERE split_part(key, '_', 1)::numeric NOT IN ({configured_server_numbers})
        """
    )

    # Split only at the first underscore because config class names may also
    # contain underscores.
    op.execute(
        """
        UPDATE user_config
        SET server_number = split_part(key, '_', 1)::integer,
            name = CASE
                WHEN substring(key FROM position('_' IN key) + 1) = 'auto_settings'
                    THEN 'AutoSettings'
                ELSE substring(key FROM position('_' IN key) + 1)
            END
        """
    )

    # User configs are owned by Alembic rather than Django. Remove the retired
    # Scorebot config here while the table is being migrated to its new schema.
    op.execute(
        """
        DELETE FROM user_config
        WHERE name = 'ScorebotUserConfig'
        """
    )

    for server_number, game_id in server_games.items():
        # Both values have been parsed as integers, so interpolating them is safe
        # and also keeps Alembic's offline SQL output usable.
        op.execute(
            f"""
            UPDATE user_config
            SET game = {game_id}
            WHERE server_number = {server_number}
            """
        )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM user_config
                WHERE game IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Cannot determine game for one or more user_config server numbers';
            END IF;
        END
        $$;
        """
    )

    op.alter_column("user_config", "server_number", nullable=False)
    op.alter_column(
        "user_config",
        "game",
        nullable=False,
        server_default="1",
    )
    op.alter_column("user_config", "name", nullable=False)
    op.create_unique_constraint(
        UNIQUE_CONSTRAINT,
        "user_config",
        ["game", "server_number", "name"],
    )
    op.drop_index("ix_user_config_key", table_name="user_config")
    op.drop_column("user_config", "key")


def downgrade():
    op.add_column(
        "user_config",
        sa.Column("key", sa.String(), nullable=True),
    )

    # The legacy schema cannot distinguish games because its unique key only
    # contains the server number and config name. Preserve the original HLL
    # (WW2) records and discard configs for games unsupported by that schema.
    op.execute(
        """
        DELETE FROM user_config
        WHERE game != 1
        """
    )

    op.execute(
        """
        UPDATE user_config
        SET key = server_number::text || '_' || CASE
            WHEN name = 'AutoSettings' THEN 'auto_settings'
            ELSE name
        END
        """
    )
    op.alter_column("user_config", "key", nullable=False)

    op.drop_constraint(UNIQUE_CONSTRAINT, "user_config", type_="unique")
    op.drop_column("user_config", "name")
    op.drop_column("user_config", "game")
    op.drop_column("user_config", "server_number")
    op.create_index(
        "ix_user_config_key",
        "user_config",
        ["key"],
        unique=True,
    )
