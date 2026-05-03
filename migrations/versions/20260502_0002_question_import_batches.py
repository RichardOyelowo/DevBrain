"""question import batches

Revision ID: 20260502_0002
Revises: 20260501_0001
Create Date: 2026-05-02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260502_0002"
down_revision = "20260501_0001"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "question_import_batches" in inspector.get_table_names():
        return

    op.create_table(
        "question_import_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_question_import_batches_user_id", "question_import_batches", ["user_id"], unique=False)


def downgrade():
    op.drop_index("ix_question_import_batches_user_id", table_name="question_import_batches")
    op.drop_table("question_import_batches")
