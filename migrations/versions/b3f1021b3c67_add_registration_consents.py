"""add registration consents

Revision ID: b3f1021b3c67
Revises: 3e607cbd94de
Create Date: 2026-02-26 09:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b3f1021b3c67"
down_revision = "3e607cbd94de"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "statute_accepted",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "wants_active_membership",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "wants_email_notifications",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column("statute_accepted", server_default=None)
        batch_op.alter_column("wants_active_membership", server_default=None)
        batch_op.alter_column("wants_email_notifications", server_default=None)


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("wants_email_notifications")
        batch_op.drop_column("wants_active_membership")
        batch_op.drop_column("statute_accepted")
