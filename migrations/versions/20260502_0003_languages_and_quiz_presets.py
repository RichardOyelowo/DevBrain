"""languages and quiz presets

Revision ID: 20260502_0003
Revises: 20260502_0002
Create Date: 2026-05-02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260502_0003"
down_revision = "20260502_0002"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "languages" not in existing_tables:
        op.create_table(
            "languages",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=80), nullable=False),
            sa.Column("slug", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
            sa.UniqueConstraint("slug"),
        )
        op.create_index("ix_languages_slug", "languages", ["slug"], unique=False)

    if "quiz_presets" not in existing_tables:
        op.create_table(
            "quiz_presets",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("topic_id", sa.Integer(), nullable=False),
            sa.Column("slug", sa.String(length=140), nullable=False),
            sa.Column("title", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("difficulty", sa.String(length=20), nullable=False),
            sa.Column("question_limit", sa.Integer(), nullable=False),
            sa.Column("language", sa.String(length=40), nullable=True),
            sa.Column("accent", sa.String(length=40), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["topic_id"], ["topics.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("slug"),
        )
        op.create_index("ix_quiz_presets_slug", "quiz_presets", ["slug"], unique=False)
        op.create_index("ix_quiz_presets_topic_id", "quiz_presets", ["topic_id"], unique=False)


def downgrade():
    op.drop_index("ix_quiz_presets_topic_id", table_name="quiz_presets")
    op.drop_index("ix_quiz_presets_slug", table_name="quiz_presets")
    op.drop_table("quiz_presets")
    op.drop_index("ix_languages_slug", table_name="languages")
    op.drop_table("languages")
