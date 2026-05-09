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

    if "quizzes" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("quizzes")}
        if "date" not in columns:
            db.session.execute(text("ALTER TABLE quizzes ADD COLUMN date DATETIME"))

    db.session.commit()
