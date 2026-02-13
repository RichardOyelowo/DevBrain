from flask import session, redirect, url_for
from flask_wtf import CSRFProtect
from functools import wraps
from flask_mail import Mail


mail = Mail()
csrf = CSRFProtect()


# ---------------- Login Required Decorator ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("auth.login"))

        return f(*args,**kwargs)

    return decorated_function