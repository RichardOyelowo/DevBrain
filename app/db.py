from sqlalchemy import inspect, text
from flask import current_app, g
from .extensions import db
import os

def get_db():
    return db.session.connection()

def close_db(e=None):
    g.pop("db", None)

def create_db():
    ensure_database_ready()


def ensure_database_ready(seed=True):
    uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    if uri.startswith("sqlite:///"):
        db_path = uri.replace("sqlite:///", "", 1)
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    db.create_all()
    _patch_existing_sqlite_schema()

    if seed:
        from .seed import seed_question_bank

        seed_question_bank()


def ensure_starter_catalog():
    from .models import Language, Question, QuizPreset, Topic
    from .seed import seed_question_bank

    missing_catalog = (
        Topic.query.count() == 0
        or Language.query.count() == 0
        or QuizPreset.query.count() == 0
        or Question.query.filter_by(source="seed").count() == 0
    )
    if missing_catalog:
        seed_question_bank()
        return True
    return False


def _patch_existing_sqlite_schema():
    if db.engine.dialect.name != "sqlite":
        return

    inspector = inspect(db.engine)
    if "users" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("users")}
        if "role" not in columns:
            db.session.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))
        if "created_at" not in columns:
            db.session.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))
        if "password_changed_at" not in columns:
            db.session.execute(text("ALTER TABLE users ADD COLUMN password_changed_at DATETIME"))
            db.session.execute(text("UPDATE users SET password_changed_at = created_at WHERE password_changed_at IS NULL"))
        if "plan" not in columns:
            db.session.execute(text("ALTER TABLE users ADD COLUMN plan VARCHAR(20) NOT NULL DEFAULT 'free'"))
        if not _sqlite_index_exists("users", "uq_users_email_lower"):
            duplicate_rows = db.session.execute(text(
                "SELECT lower(email) AS normalized_email, count(*) AS total "
                "FROM users GROUP BY lower(email) HAVING count(*) > 1"
            )).fetchall()
            if duplicate_rows:
                emails = ", ".join(row.normalized_email for row in duplicate_rows)
                raise RuntimeError(f"Resolve duplicate user emails before startup: {emails}")
            db.session.execute(text("UPDATE users SET email = lower(trim(email))"))
            db.session.execute(text("CREATE UNIQUE INDEX uq_users_email_lower ON users (lower(email))"))

    if "quizzes" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("quizzes")}
        if "date" not in columns:
            db.session.execute(text("ALTER TABLE quizzes ADD COLUMN date DATETIME"))

    db.session.commit()


def _sqlite_index_exists(table_name, index_name):
    rows = db.session.execute(text(f"PRAGMA index_list('{table_name}')")).fetchall()
    return any(row[1] == index_name for row in rows)
