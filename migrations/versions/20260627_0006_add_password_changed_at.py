"""add password changed timestamp

Revision ID: 20260627_0006
Revises: 20260525_0005
Create Date: 2026-06-27
"""

from alembic import op
import sqlalchemy as sa


revision = "20260627_0006"
down_revision = "20260525_0005"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    if "password_changed_at" not in columns:
        op.add_column("users", sa.Column("password_changed_at", sa.DateTime(), nullable=True))
        op.execute(sa.text("UPDATE users SET password_changed_at = created_at WHERE password_changed_at IS NULL"))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    if "password_changed_at" in columns:
        op.drop_column("users", "password_changed_at")
