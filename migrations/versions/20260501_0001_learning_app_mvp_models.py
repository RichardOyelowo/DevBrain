"""learning app mvp models

Revision ID: 20260501_0001
Revises:
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260501_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("username", sa.String(length=80), nullable=True),
            sa.Column("password", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )
        op.create_index("ix_users_email", "users", ["email"], unique=False)
    else:
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "role" not in user_columns:
            op.add_column("users", sa.Column("role", sa.String(length=20), nullable=False, server_default="user"))
        if "created_at" not in user_columns:
            op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))

    if "quizzes" not in existing_tables:
        op.create_table(
            "quizzes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("date", sa.DateTime(), nullable=True),
            sa.Column("topic", sa.String(length=255), nullable=True),
            sa.Column("difficulty", sa.String(length=20), nullable=True),
            sa.Column("question_count", sa.Integer(), nullable=False),
            sa.Column("score", sa.Integer(), nullable=False),
            sa.Column("grade", sa.String(length=40), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("idx_quizzes_user_id", "quizzes", ["user_id"], unique=False)

    if "topics" not in existing_tables:
        op.create_table(
            "topics",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("slug", sa.String(length=140), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
            sa.UniqueConstraint("slug"),
        )
        op.create_index("ix_topics_slug", "topics", ["slug"], unique=False)

    if "questions" not in existing_tables:
        op.create_table(
            "questions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("topic_id", sa.Integer(), nullable=False),
            sa.Column("prompt", sa.Text(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("explanation", sa.Text(), nullable=True),
            sa.Column("difficulty", sa.String(length=20), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("is_archived", sa.Boolean(), nullable=False),
            sa.Column("language", sa.String(length=40), nullable=True),
            sa.Column("code_snippet", sa.Text(), nullable=True),
            sa.Column("source", sa.String(length=40), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["topic_id"], ["topics.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_questions_difficulty", "questions", ["difficulty"], unique=False)
        op.create_index("ix_questions_is_archived", "questions", ["is_archived"], unique=False)
        op.create_index("ix_questions_status", "questions", ["status"], unique=False)
        op.create_index("ix_questions_topic_id", "questions", ["topic_id"], unique=False)

    if "answer_options" not in existing_tables:
        op.create_table(
            "answer_options",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("question_id", sa.Integer(), nullable=False),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("is_correct", sa.Boolean(), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["question_id"], ["questions.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_answer_options_question_id", "answer_options", ["question_id"], unique=False)

    if "quiz_attempts" not in existing_tables:
        op.create_table(
            "quiz_attempts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("topic_id", sa.Integer(), nullable=True),
            sa.Column("topic_label", sa.String(length=255), nullable=False),
            sa.Column("difficulty", sa.String(length=20), nullable=False),
            sa.Column("question_count", sa.Integer(), nullable=False),
            sa.Column("score", sa.Integer(), nullable=False),
            sa.Column("grade", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["topic_id"], ["topics.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_quiz_attempts_topic_id", "quiz_attempts", ["topic_id"], unique=False)
        op.create_index("ix_quiz_attempts_user_id", "quiz_attempts", ["user_id"], unique=False)

    if "quiz_attempt_answers" not in existing_tables:
        op.create_table(
            "quiz_attempt_answers",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("attempt_id", sa.Integer(), nullable=False),
            sa.Column("question_id", sa.Integer(), nullable=False),
            sa.Column("selected_option_id", sa.Integer(), nullable=True),
            sa.Column("is_correct", sa.Boolean(), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("answered_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["attempt_id"], ["quiz_attempts.id"]),
            sa.ForeignKeyConstraint(["question_id"], ["questions.id"]),
            sa.ForeignKeyConstraint(["selected_option_id"], ["answer_options.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_quiz_attempt_answers_attempt_id", "quiz_attempt_answers", ["attempt_id"], unique=False)
        op.create_index("ix_quiz_attempt_answers_question_id", "quiz_attempt_answers", ["question_id"], unique=False)

    if "ai_generation_requests" not in existing_tables:
        op.create_table(
            "ai_generation_requests",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("topic_id", sa.Integer(), nullable=False),
            sa.Column("difficulty", sa.String(length=20), nullable=False),
            sa.Column("count", sa.Integer(), nullable=False),
            sa.Column("code_style", sa.String(length=80), nullable=True),
            sa.Column("provider", sa.String(length=80), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["topic_id"], ["topics.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ai_generation_requests_user_id", "ai_generation_requests", ["user_id"], unique=False)


def downgrade():
    for table_name in [
        "ai_generation_requests",
        "quiz_attempt_answers",
        "quiz_attempts",
        "answer_options",
        "questions",
        "topics",
    ]:
        op.drop_table(table_name)
