"""add project custom page

Revision ID: 4d5e6f7a8b9c
Revises: 1c3d4e5f6a7b
Create Date: 2026-04-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d5e6f7a8b9c"
down_revision = "1c3d4e5f6a7b"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("project", schema=None) as batch_op:
        batch_op.add_column(sa.Column("custom_page_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("custom_page_html", sa.Text(), nullable=True))

    op.execute("UPDATE project SET custom_page_enabled = FALSE WHERE custom_page_enabled IS NULL")

    with op.batch_alter_table("project", schema=None) as batch_op:
        batch_op.alter_column("custom_page_enabled", server_default=None)


def downgrade():
    with op.batch_alter_table("project", schema=None) as batch_op:
        batch_op.drop_column("custom_page_html")
        batch_op.drop_column("custom_page_enabled")
