"""Split user_config key into game, server number, and name.

Revision ID: 3f12a7b9c4d1
Revises: 70d823b91325
Create Date: 2026-08-17

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3f12a7b9c4d1"
down_revision = "70d823b91325"
branch_labels = None
depends_on = None


UNIQUE_CONSTRAINT = "uq_user_config_game_server_number_name"


def upgrade():
    op.add_column(
        "user_config",
        sa.Column("server_number", sa.Integer(), nullable=True),
    )
    op.add_column(
        "user_config",
        sa.Column(
            "game",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )
    op.add_column(
        "user_config",
        sa.Column("name", sa.String(), nullable=True),
    )

    # Fail with a useful error instead of silently producing invalid data or
    # failing later while converting the server number to an integer.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM user_config
                WHERE key IS NULL OR key !~ '^[0-9]+_.+$'
            ) THEN
                RAISE EXCEPTION
                    'Cannot split malformed user_config key; expected {server_number}_{name}';
            END IF;
        END
        $$;
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

    op.alter_column("user_config", "server_number", nullable=False)
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
