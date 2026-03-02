"""add google form url to article

Revision ID: 8f6f0f3f6a21
Revises: 6b93f9d8f0c1
Create Date: 2026-03-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f6f0f3f6a21"
down_revision = "6b93f9d8f0c1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("article", schema=None) as batch_op:
        batch_op.add_column(sa.Column("google_form_url", sa.String(length=1000), nullable=True))


def downgrade():
    with op.batch_alter_table("article", schema=None) as batch_op:
        batch_op.drop_column("google_form_url")
