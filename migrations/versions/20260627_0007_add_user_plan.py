"""add user plan

Revision ID: 20260627_0007
Revises: 20260627_0006
Create Date: 2026-06-27
"""

from alembic import op
import sqlalchemy as sa


revision = "20260627_0007"
down_revision = "20260627_0006"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    if "plan" not in columns:
        op.add_column("users", sa.Column("plan", sa.String(length=20), nullable=False, server_default="free"))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    if "plan" in columns:
        op.drop_column("users", "plan")
