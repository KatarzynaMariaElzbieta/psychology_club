"""add mailing batches

Revision ID: d2a6a1a9d4c2
Revises: 13a4c6e9b2d1
Create Date: 2026-03-13 12:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d2a6a1a9d4c2"
down_revision = "13a4c6e9b2d1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mailing_batch",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("template_id", sa.String(length=120), nullable=False),
        sa.Column("visible_to_email", sa.String(length=255), nullable=False),
        sa.Column("visible_to_name", sa.String(length=120), nullable=True),
        sa.Column("send_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("total_recipients", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("stored_name", sa.String(length=255), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("auto_delete", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("stored_name"),
    )


def downgrade():
    op.drop_table("mailing_batch")
