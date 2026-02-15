from flask import session, redirect, url_for
from flask_wtf import CSRFProtect
from functools import wraps
from flask_mail import Mail
import redis
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


# ---------------- Redis Client for Quiz ----------------
REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
else:
    redis_client = redis.Redis(host="localhost", port=6379, db=0)

quiz_cache = redis_client