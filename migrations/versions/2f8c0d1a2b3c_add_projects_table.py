"""add projects table

Revision ID: 2f8c0d1a2b3c
Revises: 13a4c6e9b2d1
Create Date: 2026-04-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2f8c0d1a2b3c"
down_revision = "13a4c6e9b2d1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("project_type", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=600), nullable=False),
        sa.Column("extra_content", sa.Text(), nullable=True),
        sa.Column("responsible_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["responsible_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("project")
