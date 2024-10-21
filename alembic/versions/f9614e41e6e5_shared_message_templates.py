"""Shared message templates

Revision ID: f9614e41e6e5
Revises: f48c611a3f56
Create Date: 2024-09-30 18:17:46.775392

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f9614e41e6e5"
down_revision = "f48c611a3f56"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "message_template",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "MESSAGE",
                "BROADCAST",
                "WELCOME",
                "REASON",
                name="message_template_category",
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("message_template")
    op.execute("DROP TYPE message_template_category")
