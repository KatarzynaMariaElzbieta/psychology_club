"""add form close date to article

Revision ID: 13a4c6e9b2d1
Revises: 8f6f0f3f6a21
Create Date: 2026-03-02 12:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "13a4c6e9b2d1"
down_revision = "8f6f0f3f6a21"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("article", schema=None) as batch_op:
        batch_op.add_column(sa.Column("form_closes_at", sa.Date(), nullable=True))


def downgrade():
    with op.batch_alter_table("article", schema=None) as batch_op:
        batch_op.drop_column("form_closes_at")
