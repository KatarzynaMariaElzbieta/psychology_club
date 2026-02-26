"""add image consent

Revision ID: c91dc8d947ad
Revises: b3f1021b3c67
Create Date: 2026-02-26 09:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c91dc8d947ad"
down_revision = "b3f1021b3c67"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "image_consent",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column("image_consent", server_default=None)


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("image_consent")
