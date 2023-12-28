"""Remove timezones

Revision ID: ed4f14f06c39
Revises: 22e3790f2095
Create Date: 2023-12-28 18:26:21.288906

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.types import TIMESTAMP

# revision identifiers, used by Alembic.
revision = "ed4f14f06c39"
down_revision = "22e3790f2095"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("player_vip", "expiration", type_=TIMESTAMP)
    op.alter_column("audit_log", "creation_time", type_=TIMESTAMP)


def downgrade():
    op.alter_column("player_vip", "expiration", type_=TIMESTAMP(timezone=True))
    op.alter_column("audit_log", "creation_time", type_=TIMESTAMP(timezone=True))
