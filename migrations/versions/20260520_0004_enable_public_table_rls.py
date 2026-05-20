"""enable rls on public app tables

Revision ID: 20260520_0004
Revises: 20260502_0003
Create Date: 2026-05-20
"""

from alembic import op
import sqlalchemy as sa


revision = "20260520_0004"
down_revision = "20260502_0003"
branch_labels = None
depends_on = None


PUBLIC_TABLES = (
    "alembic_version",
    "users",
    "quizzes",
    "topics",
    "questions",
    "answer_options",
    "quiz_attempts",
    "quiz_attempt_answers",
    "question_import_batches",
    "languages",
    "quiz_presets",
)


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names(schema="public"))

    for table_name in PUBLIC_TABLES:
        if table_name in existing_tables:
            op.execute(sa.text(f'ALTER TABLE public."{table_name}" ENABLE ROW LEVEL SECURITY'))


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names(schema="public"))

    for table_name in PUBLIC_TABLES:
        if table_name in existing_tables:
            op.execute(sa.text(f'ALTER TABLE public."{table_name}" DISABLE ROW LEVEL SECURITY'))
