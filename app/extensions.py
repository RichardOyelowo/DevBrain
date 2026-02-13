from flask_mail import Message, Mail
from functools import wraps
from flask_wtf import CSRFProtect
import sqlite3


csrf = CSRFProtect()
mail = Mail()


def create_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    if not os.path.exists(DATABASE_PATH):
        with sqlite3.connect(DATABASE_PATH) as conn:
            with open("schema.sql", "r") as f:
                conn.executescript(f.read())


def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row

    return conn


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function
