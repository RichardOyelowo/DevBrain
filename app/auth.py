from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import mail, login_required
from .forms import Register, Login, ForgotPassword, ResetPassword
from flask_mail import Message
from .db import get_db
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, current_app
)


auth = Blueprint("auth", __name__)


# ---------------- Reset Email Utility ----------------
def send_reset_email(to_email, reset_link):
    """Send password reset email using Flask-Mail and app config"""

    msg = Message(
        subject="Reset Your DevBrain Password",
        recipients= [to_email],
        html=render_template("reset_email.html", reset_link=reset_link),
        body=render_template("reset_email.txt", reset_link=reset_link)
    )
    mail.send(msg)

def get_serializer():
    """Helper to get URLSafeTimedSerializer using app's SECRET_KEY"""
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


# ---------------- Registration ----------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    form = Register()

    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data

        conn = get_db()
        cur = conn.cursor()
        
        if cur.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone():    
            conn.close()
            flash("Email already exists","danger")

            return redirect(url_for("auth.login"))

        cur.execute(
            "INSERT INTO users (email, username, password) VALUES (?, ?, ?)",
            (email, username, generate_password_hash(password))
        )
        conn.commit()
        user_id = cur.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"]
        conn.close()

        session["user_id"] = user_id
        return redirect(url_for("main.quiz"))

    return render_template("register.html", form=form)


# ---------------- Login ----------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    form = Login()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        conn = get_db()
        cur = conn.cursor()
        row = cur.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if not row or not check_password_hash(row["password"], password):
            flash("Invalid email or password", "info")
            return render_template("login.html", form=form)

        session["user_id"] = row["id"]
        return redirect(url_for("main.quiz"))

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

        conn = get_db()
        cur = conn.cursor()
        row = cur.execute("SELECT * FROM users WHERE email = ?", (users_email,)).fetchone()
        conn.close()

        if row:
            s = get_serializer()
            token = s.dumps(row["id"], salt="password-reset-salt")
            reset_link = url_for("auth.reset_password", token=token, _external=True)
            try:
                send_reset_email(to_email=row["email"], reset_link=reset_link)
            except Exception as e:
                return render_template("forgot_password.html", form_type="forgot", error="Error sending email. Try again later.", form=form)

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
        return render_template("forgot_password.html", form_type="forgot", error="The reset link is invalid or expired.")

    if form.validate_on_submit():
        new_password = form.password.data

        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = ? WHERE id = ?",
                    (generate_password_hash(new_password), user_id))
        conn.commit()
        conn.close()

        return render_template("forgot_password.html", form_type="success")

    return render_template("forgot_password.html", form_type="reset", token=token, form=form)
