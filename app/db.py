import sqlite3
from flask import current_app

def get_db():
    conn = sqlite3.connect(current_app.config["DATABASE_URL"])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    import os

    db_path = current_app.config.get("DATABASE_URL")
    if not db_path:
        raise RuntimeError("DATABASE_URL not configured")

    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    if not os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            with open("app/schema.sql", "r", encoding="utf-8") as f:
                conn.executescript(f.read())
