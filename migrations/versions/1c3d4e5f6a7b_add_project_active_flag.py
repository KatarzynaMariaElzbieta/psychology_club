"""add project active flag

Revision ID: 1c3d4e5f6a7b
Revises: 8bbf94bc23b2
Create Date: 2026-04-03 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1c3d4e5f6a7b"
down_revision = "8bbf94bc23b2"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("project", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))

    op.execute("UPDATE project SET is_active = TRUE WHERE is_active IS NULL")

    with op.batch_alter_table("project", schema=None) as batch_op:
        batch_op.alter_column("is_active", server_default=None)


def downgrade():
    with op.batch_alter_table("project", schema=None) as batch_op:
        batch_op.drop_column("is_active")
