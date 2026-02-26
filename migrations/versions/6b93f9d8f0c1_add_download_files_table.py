"""add download files table

Revision ID: 6b93f9d8f0c1
Revises: c91dc8d947ad
Create Date: 2026-02-26 12:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6b93f9d8f0c1"
down_revision = "c91dc8d947ad"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "download_file",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=600), nullable=True),
        sa.Column("stored_name", sa.String(length=255), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_name"),
    )


def downgrade():
    op.drop_table("download_file")
