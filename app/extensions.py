from flask import session, redirect, url_for
from flask_wtf import CSRFProtect
from functools import wraps
from flask_mail import Mail
from redis import Redis
import os

mail = Mail()
csrf = CSRFProtect()


# ---------------- Login Required Decorator ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("auth.login"))
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
