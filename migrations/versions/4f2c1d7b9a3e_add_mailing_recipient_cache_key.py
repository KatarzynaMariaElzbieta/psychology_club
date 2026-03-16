"""add mailing recipient cache key

Revision ID: 4f2c1d7b9a3e
Revises: 7a8b6f2c1d4e
Create Date: 2026-03-13 15:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4f2c1d7b9a3e"
down_revision = "7a8b6f2c1d4e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("mailing_batch", sa.Column("recipient_cache_key", sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column("mailing_batch", "recipient_cache_key")
