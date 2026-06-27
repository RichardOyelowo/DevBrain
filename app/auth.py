from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import Register, Login, ForgotPassword, ResetPassword
from .extensions import db, mail, login_required
from flask_mail import Message
from .models import User
import socket
import threading
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, current_app
)


auth = Blueprint("auth", __name__)


# ---------------- Reset Email Utility ----------------
def build_reset_email(to_email, reset_link):
    return Message(
        subject="Reset Your DevBrain Password",
        recipients= [to_email],
        html=render_template("reset_email.html", reset_link=reset_link),
        body=render_template("reset_email.txt", reset_link=reset_link)
    )


def send_prepared_email(msg):
    previous_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(current_app.config.get("MAIL_TIMEOUT", 8))
    try:
        mail.send(msg)
    finally:
        socket.setdefaulttimeout(previous_timeout)


def send_reset_email(to_email, reset_link):
    """Send password reset email using Flask-Mail and app config"""

    send_prepared_email(build_reset_email(to_email, reset_link))


def queue_reset_email(to_email, reset_link, user_id):
    app = current_app._get_current_object()
    msg = build_reset_email(to_email, reset_link)
    timeout = current_app.config.get("MAIL_TIMEOUT", 8)

    def _send():
        with app.app_context():
            app.config["MAIL_TIMEOUT"] = timeout
            try:
                send_prepared_email(msg)
            except Exception:
                app.logger.exception("Password reset email failed for user %s", user_id)

    threading.Thread(target=_send, daemon=True).start()

def get_serializer():
    """Helper to get URLSafeTimedSerializer using app's SECRET_KEY"""
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def registration_role():
    if User.query.count() == 0 and current_app.config.get("ADMIN_BOOTSTRAP_ENABLED"):
        return "admin"
    return "user"


# ---------------- Registration ----------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    form = Register()

    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash("Email already exists","danger")
            return redirect(url_for("auth.login"))

        user = User(
            email=email,
            username=username,
            password=generate_password_hash(password),
            role=registration_role(),
        )
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        return redirect(url_for("main.dashboard"))

    return render_template("register.html", form=form)


# ---------------- Login ----------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    form = Login()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password", "info")
            return render_template("login.html", form=form)

        session["user_id"] = user.id
        return redirect(url_for("main.dashboard"))

    return render_template("login.html", form=form)


# ---------------- Logout ----------------
@auth.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# ---------------- Forgot Password ----------------
@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPassword()
    
    if form.validate_on_submit():
        users_email = form.email.data

        user = User.query.filter_by(email=users_email).first()

        if user:
            s = get_serializer()
            token = s.dumps(user.id, salt="password-reset-salt")
            reset_link = url_for("auth.reset_password", token=token, _external=True)
            queue_reset_email(to_email=user.email, reset_link=reset_link, user_id=user.id)

        return render_template("forgot_password.html", form_type="sent_or_notfound")

    return render_template("forgot_password.html", form_type="forgot", form=form)


# ---------------- Reset Password ----------------
@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPassword()

    s = get_serializer()
    try:
        user_id = s.loads(token, salt="password-reset-salt", max_age=3600)
    except (BadSignature, SignatureExpired):
        return render_template(
            "forgot_password.html",
            form_type="forgot",
            error="The reset link is invalid or expired.",
            form=ForgotPassword(),
        )

    if form.validate_on_submit():
        new_password = form.password.data

        user = db.session.get(User, user_id)
        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()

        return render_template("forgot_password.html", form_type="success")

    return render_template("forgot_password.html", form_type="reset", token=token, form=form)
