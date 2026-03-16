"""add mailing template types

Revision ID: 7a8b6f2c1d4e
Revises: 5b7fdc6e1c9a
Create Date: 2026-03-13 14:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7a8b6f2c1d4e"
down_revision = "5b7fdc6e1c9a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mailing_template_type",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("template_id", sa.String(length=120), nullable=False),
        sa.Column("fields", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.add_column("mailing_batch", sa.Column("template_type_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_mailing_batch_template_type",
        "mailing_batch",
        "mailing_template_type",
        ["template_type_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("fk_mailing_batch_template_type", "mailing_batch", type_="foreignkey")
    op.drop_column("mailing_batch", "template_type_id")
    op.drop_table("mailing_template_type")
