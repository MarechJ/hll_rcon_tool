"""vip_list_record_player_id_constraint

Revision ID: 70253d0084df
Revises: c8b8a0bf2c8f
Create Date: 2025-02-27 19:35:42.044871

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "70253d0084df"
down_revision = "c8b8a0bf2c8f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "unique_vip_player_id_vip_list",
        "vip_list_record",
        ["id", "player_id_id", "vip_list_id"],
    )


def downgrade():
    op.drop_constraint(
        "unique_vip_player_id_vip_list", "vip_list_record", type_="unique"
    )
