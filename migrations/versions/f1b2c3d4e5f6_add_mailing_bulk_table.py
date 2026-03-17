"""add mailing bulk table

Revision ID: f1b2c3d4e5f6
Revises: d2a6a1a9d4c2
Create Date: 2026-03-17 10:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f1b2c3d4e5f6"
down_revision = "9c1e7d2a4b6f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mailing_bulk",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("mailing_batch.id"), nullable=False),
        sa.Column("bulk_email_id", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="queued"),
        sa.Column("state", sa.String(length=24), nullable=True),
        sa.Column("total_recipients", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_checked_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("bulk_email_id"),
    )
    op.create_index("ix_mailing_bulk_batch_id", "mailing_bulk", ["batch_id"])


def downgrade():
    op.drop_index("ix_mailing_bulk_batch_id", table_name="mailing_bulk")
    op.drop_table("mailing_bulk")
