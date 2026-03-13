"""add mailing subjects

Revision ID: 9c1e7d2a4b6f
Revises: 4f2c1d7b9a3e
Create Date: 2026-03-13 16:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9c1e7d2a4b6f"
down_revision = "4f2c1d7b9a3e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("mailing_batch", sa.Column("subject", sa.String(length=255), nullable=False, server_default=""))


def downgrade():
    op.drop_column("mailing_batch", "subject")
