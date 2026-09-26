"""Allow an explicit never-expiring VIP list default.

Revision ID: c4e9a6b183d2
Revises: af731c89d215
"""

from alembic import op

revision = "c4e9a6b183d2"
down_revision = "af731c89d215"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("vip_list_default_expiration_seconds_positive", "vip_list")
    op.create_check_constraint(
        "vip_list_default_expiration_seconds_nonnegative",
        "vip_list",
        "default_expiration_seconds >= 0",
    )


def downgrade():
    op.execute(
        "UPDATE vip_list SET default_expiration_seconds = NULL "
        "WHERE default_expiration_seconds = 0"
    )
    op.drop_constraint("vip_list_default_expiration_seconds_nonnegative", "vip_list")
    op.create_check_constraint(
        "vip_list_default_expiration_seconds_positive",
        "vip_list",
        "default_expiration_seconds > 0",
    )
