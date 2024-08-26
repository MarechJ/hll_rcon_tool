"""added comment author

Revision ID: 066d4f72edd8
Revises: dd31e8743d7e
Create Date: 2021-05-16 13:15:41.008152

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "066d4f72edd8"
down_revision = "dd31e8743d7e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("player_comments", sa.Column("by", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("player_comments", "by")
    # ### end Alembic commands ###
