"""Update message template enum

Revision ID: 1e8fd0c19cb0
Revises: f9614e41e6e5
Create Date: 2024-10-29 18:37:09.613989

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e8fd0c19cb0'
down_revision = 'f9614e41e6e5'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE message_template_category ADD VALUE IF NOT EXISTS 'AUTO_SETTINGS';")


def downgrade():
    pass
