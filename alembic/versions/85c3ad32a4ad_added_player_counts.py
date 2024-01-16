"""Added player counts

Revision ID: 85c3ad32a4ad
Revises: 066d4f72edd8
Create Date: 2022-01-06 17:40:59.017700

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "85c3ad32a4ad"
down_revision = "066d4f72edd8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "server_counts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("server_number", sa.Integer(), nullable=True),
        sa.Column("creation_time", sa.TIMESTAMP(), nullable=True),
        sa.Column("datapoint_time", sa.TIMESTAMP(), nullable=True),
        sa.Column("map_id", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["map_id"],
            ["map_history.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("datapoint_time"),
        sa.UniqueConstraint(
            "server_number", "datapoint_time", name="unique_server_count"
        ),
    )
    op.create_index(
        op.f("ix_server_counts_map_id"), "server_counts", ["map_id"], unique=False
    )
    op.create_table(
        "player_at_count",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("playersteamid_id", sa.Integer(), nullable=False),
        sa.Column("servercount_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["playersteamid_id"],
            ["steam_id_64.id"],
        ),
        sa.ForeignKeyConstraint(
            ["servercount_id"],
            ["server_counts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_player_at_count_playersteamid_id"),
        "player_at_count",
        ["playersteamid_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_player_at_count_servercount_id"),
        "player_at_count",
        ["servercount_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_player_at_count_servercount_id"), table_name="player_at_count"
    )
    op.drop_index(
        op.f("ix_player_at_count_playersteamid_id"), table_name="player_at_count"
    )
    op.drop_table("player_at_count")
    op.drop_index(op.f("ix_server_counts_map_id"), table_name="server_counts")
    op.drop_table("server_counts")
    # ### end Alembic commands ###
