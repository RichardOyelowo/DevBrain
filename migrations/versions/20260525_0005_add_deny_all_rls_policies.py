"""add deny all rls policies

Revision ID: 20260525_0005
Revises: 20260520_0004
Create Date: 2026-05-25
"""

from alembic import op
import sqlalchemy as sa


revision = "20260525_0005"
down_revision = "20260520_0004"
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

POLICY_NAME = "deny_anon_authenticated_access"


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names(schema="public"))

    for table_name in PUBLIC_TABLES:
        if table_name not in existing_tables:
            continue
        op.execute(
            sa.text(
                f'DROP POLICY IF EXISTS "{POLICY_NAME}" ON public."{table_name}"'
            )
        )
        op.execute(
            sa.text(
                f'CREATE POLICY "{POLICY_NAME}" ON public."{table_name}" '
                "FOR ALL TO anon, authenticated "
                "USING (false) WITH CHECK (false)"
            )
        )


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names(schema="public"))

    for table_name in PUBLIC_TABLES:
        if table_name in existing_tables:
            op.execute(
                sa.text(
                    f'DROP POLICY IF EXISTS "{POLICY_NAME}" ON public."{table_name}"'
                )
            )
