"""add case-insensitive user email index

Revision ID: 20260628_0008
Revises: 20260627_0007
Create Date: 2026-06-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260628_0008"
down_revision = "20260627_0007"
branch_labels = None
depends_on = None


INDEX_NAME = "uq_users_email_lower"


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("users")}

    if INDEX_NAME not in indexes:
        duplicate_rows = bind.execute(sa.text(
            "SELECT lower(email) AS normalized_email, count(*) AS total "
            "FROM users GROUP BY lower(email) HAVING count(*) > 1"
        )).fetchall()
        if duplicate_rows:
            emails = ", ".join(row.normalized_email for row in duplicate_rows)
            raise RuntimeError(f"Resolve duplicate user emails before migration: {emails}")

        op.execute(sa.text("UPDATE users SET email = lower(trim(email))"))
        op.execute(sa.text(f"CREATE UNIQUE INDEX {INDEX_NAME} ON users (lower(email))"))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("users")}

    if INDEX_NAME in indexes:
        op.drop_index(INDEX_NAME, table_name="users")
