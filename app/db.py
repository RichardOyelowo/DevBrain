import sqlite3
import os
from flask import current_app, g

def get_db():
    """
    Get a per-request SQLite connection.
    Uses WAL mode and check_same_thread=False for multi-worker safety.
    """
    if "db" not in g:
        db_path = current_app.config["DATABASE_URL"]
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False  # allow multiple threads/workers
        )
        g.db.row_factory = sqlite3.Row
        # Enable WAL mode for concurrent reads/writes
        g.db.execute("PRAGMA journal_mode=WAL;")
    return g.db

def close_db(e=None):
    """
    Close the per-request database connection.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()

def create_db():
    """
    Create the database file and tables if they don't exist.
    Keeps your exact schema and logic.
    """
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
