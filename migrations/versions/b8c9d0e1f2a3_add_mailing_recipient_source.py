"""add mailing recipient source

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-03-29 11:25:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b8c9d0e1f2a3"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "mailing_batch",
        sa.Column("recipient_source", sa.String(length=24), nullable=False, server_default="file"),
    )
    op.execute("UPDATE mailing_batch SET recipient_source = 'file' WHERE recipient_source IS NULL")


def downgrade():
    op.drop_column("mailing_batch", "recipient_source")
