"""add mailing template data

Revision ID: 5b7fdc6e1c9a
Revises: d2a6a1a9d4c2
Create Date: 2026-03-13 13:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5b7fdc6e1c9a"
down_revision = "d2a6a1a9d4c2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("mailing_batch", sa.Column("template_data", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("mailing_batch", "template_data")
