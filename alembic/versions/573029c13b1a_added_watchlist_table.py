"""Added watchlist table

Revision ID: 573029c13b1a
Revises: 67e97402fd6b
Create Date: 2021-01-12 01:01:34.967150

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "573029c13b1a"
down_revision = "67e97402fd6b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "player_watchlist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("playersteamid_id", sa.Integer(), nullable=False),
        sa.Column("is_watched", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("comment", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["playersteamid_id"],
            ["steam_id_64.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_player_watchlist_playersteamid_id"),
        "player_watchlist",
        ["playersteamid_id"],
        unique=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_player_watchlist_playersteamid_id"), table_name="player_watchlist"
    )
    op.drop_table("player_watchlist")
    # ### end Alembic commands ###
