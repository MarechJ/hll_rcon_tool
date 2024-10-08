"""player_stats_death_by_weapon

Revision ID: 028dee0924c2
Revises: ffdd9ef91ad9
Create Date: 2023-04-11 10:43:56.078886

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "028dee0924c2"
down_revision = "ffdd9ef91ad9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        op.f("ix_audit_log_command"), "audit_log", ["command"], unique=False
    )
    op.add_column(
        "player_stats",
        sa.Column(
            "death_by_weapons", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("player_stats", "death_by_weapons")
    op.drop_index(op.f("ix_audit_log_command"), table_name="audit_log")
    # ### end Alembic commands ###
