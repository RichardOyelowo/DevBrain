import sqlite3
from flask import session, request, render_template, redirect, url_for, Blueprint, current_app
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from config import DATABASE_URL, EMAIL, EMAIL_PASSWORD
from functools import wraps
from flask_mail import Mail, Message
import smtplib

auth = Blueprint("auth", __name__)

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

# ---------------- Reset Email Utility ----------------
mail = Mail()
def send_reset_email(to_email, reset_link, sender_email):
    msg = Message(
        subject="DevBrain Password Reset",
        recipients=[to_email],
        body=f"Reset your password: {reset_link}",
        sender=sender_email
    )
    mail.send(msg)
    

# ---------------- Registration ----------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username") or None
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not email or not password or not confirmation:
            return render_template("register.html", error="Fill all details")

        if password != confirmation:
            return render_template("register.html", error="Passwords do not match")

        conn = get_db()
        cur = conn.cursor()

        # Check if email exists
        if cur.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone():
            conn.close()
            return render_template("register.html", error="Email already exists")

        cur.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", 
                    (email, username, generate_password_hash(password)))
        conn.commit()
        user_id = cur.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"]
        conn.close()

        session["user_id"] = user_id
        
        return redirect(url_for("quiz"))

    return render_template("register.html")


# ---------------- Login ----------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="Fill all details")

        conn = get_db()
        cur = conn.cursor()
        row = cur.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if row is None or not check_password_hash(row["password"], password):
            return render_template("login.html", error="Invalid email or password")

        session["user_id"] = row["id"]

        return redirect(url_for("quiz"))

    return render_template("login.html", error=None)


# ---------------- Logout ----------------
@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# ---------------- Forgot Password ----------------
@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    token = None
    if request.method == "POST":
        users_email = request.form.get("email")

        if not users_email:
            return render_template("forgot_password.html", form_type="forgot", token=token, error="Please enter your email.")

        conn = get_db()
        cur = conn.cursor()
        row = cur.execute("SELECT * FROM users WHERE email = ?", (users_email,)).fetchone()
        conn.close()

        if row: # Send email only if user exists
            s = URLSafeTimedSerializer(current_app.secret_key)
            token = s.dumps(row["id"], salt="password-reset-salt")
            reset_link = url_for("auth.reset_password", token=token, _external=True)

            # Send reset email
            try:
                send_reset_email(to_email=users_email, reset_link=reset_link, sender_email=EMAIL)
            except:
                return render_template("forgot_password.html", form_type="forgot", token=token, error="Please try again later, some error encountered.")

        # Always show the same message for security
        return render_template("forgot_password.html", form_type="sent_or_notfound", token=None, error=None)

    return render_template("forgot_password.html", form_type="forgot", token=None, error=None)


# ---------------- Reset Password ----------------
@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.secret_key)
    try:
        user_id = s.loads(token, salt="password-reset-salt", max_age=3600)
    except Exception:
        return render_template("forgot_password.html", form_type="forgot", token=None, error="The reset link is invalid or has expired.")

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not new_password or not confirm_password:
            return render_template("forgot_password.html", form_type="reset", token=token, error="Please fill in all fields.")
        if new_password != confirm_password:
            return render_template("forgot_password.html", form_type="reset", token=token, error="Passwords do not match.")
        if len(new_password) < 8:
            return render_template("forgot_password.html", form_type="reset", token=token, error="Password must be at least 8 characters long.")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = ? WHERE id = ?", 
                    (generate_password_hash(new_password), user_id))
        conn.commit()
        conn.close()

        return render_template("forgot_password.html", form_type="success", token=None, error=None)

    return render_template("forgot_password.html", form_type="reset", token=token, error=None)
