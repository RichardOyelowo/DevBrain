from flask import flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_mail import Mail
from functools import wraps
from redis import Redis
import os

mail = Mail()
csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()


# ---------------- Login Required Decorator ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            return redirect(url_for("auth.login"))
        from .models import User
        from .session_security import auth_marker

        user = db.session.get(User, user_id)
        if not user or session.get("auth_marker") != auth_marker(user):
            session.clear()
            flash("Please log in again.", "info")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            return redirect(url_for("auth.login"))

        from .models import User
        from .session_security import auth_marker

        user = db.session.get(User, user_id)
        if not user or session.get("auth_marker") != auth_marker(user):
            session.clear()
            flash("Please log in again.", "info")
            return redirect(url_for("auth.login"))
        if not user or user.role != "admin":
            flash("You need an admin account to open that page.", "danger")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------- Redis Clients ----------------
REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL:
    # Client for Flask-Session (binary data, NO decode_responses)
    redis_client = Redis.from_url(REDIS_URL, decode_responses=False)
    
    # Client for quiz cache (JSON strings, WITH decode_responses)
    quiz_cache = Redis.from_url(REDIS_URL, decode_responses=True)
else:
    # Local Redis fallback
    redis_client = Redis(host="localhost", port=6379, db=0, decode_responses=False)
    quiz_cache = Redis(host="localhost", port=6379, db=0, decode_responses=True)
