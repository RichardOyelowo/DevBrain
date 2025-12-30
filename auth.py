import sqlite3
from flask import session, request,render_template, redirect, url_for, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import DATABASE_URL
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


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not email or not password or not confirmation:
            return render_template("register.html", error="Fill all details")

        if password != confirmation:
            return render_template("register.html", error="Passwords do not match")

        conn = get_db()
        cur = conn.cursor()

        # Check if email already exists
        existing = cur.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if existing is not None:
            conn.close() # Close the database connection
            return render_template("register.html", error="email already exists")

        # Insert new user into the database
        cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, generate_password_hash(password)))
        conn.commit()

        row = cur.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        conn.close() # Close the database connection

        session["user_id"] = row["id"]

        return redirect(url_for("index"))

    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():

    session.clear() # forget previous user

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="Fill all details")

        conn = get_db()
        cur = conn.cursor()

        row = cur.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close() # Close the database connection

        if row is None or not check_password_hash(row["password"], password):
            return render_template("login.html", error="Invalid email or password")

        session["user_id"] = row["id"]

        return redirect(url_for("index"))

    return render_template("login.html", error=None)


def logout():
    # clear user session
    session.clear()

    return redirect("/")


@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    """ I use the same route for both 'rendering the form and handling the form submission'
     1. If the request method is POST, it means the user has submitted the form, so we generate 
     a token using URLSafeTimedSerializer from itsdangerous lib then appemd that to the reset 
     link(password change page) and send it to the user's email.

     2. If the request method is GET, it means the user is accessing the page to reset their password.
     
     3. Check reset_password route to see the handling of the reset link."""

    if request.method == "POST":
        users_email = request.form.get("email")
        if not users_email:
            return render_template("forgot_password.html", form_type="forgot", error="Please enter your email address.")

        # Check if email exists in the database
        conn = get_db()
        cur = conn.cursor()
        row = cur.execute("SELECT * FROM users WHERE email = ?", (users_email,)).fetchone()

        if row is None:
            return render_template("forgot_password.html", form_type="forgot", error="Email address not found.")
        conn.close()

        # generate a token for a user_id
        s = URLSafeTimedSerializer(app.secret_key)
        user_id = row["id"] 
        token = s.dumps(user_id, salt="password-reset-salt")
        reset_link = url_for("reset_password", token=token, _external=True)
        
        #send reset link to email
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL, EMAIL_PASSWORD)
            smtp.sendmail(
                from_addr=EMAIL, to_addrs=users_email, 
                msg=f"Subject: Your Devbrain Reset Link\n\nReset your password: {reset_link}")

        return render_template("forgot_password.html", form_type="reset", message="A password reset link has been sent to your email.")
    
    # Renders the forgot password form (get method)
    return render_template("forgot_password.html", form_type="forgot")


@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Handles password reset using the token sent to user's email."""
    s = URLSafeTimedSerializer(auth.secret_key)
    try:
        user_id = s.loads(token, salt="password-reset-salt", max_age=3600)  # Token valid for 1 hour
    except Exception as e:
        return render_template("reset_password.html", form_type="forgot", error="The reset link is invalid or has expired.")

    if request.method == "POST":
        new_password = request.form.get("password")
        if not new_password:
            return render_template("reset_password.html", form_type="reset", error="Please enter a new password.")

        if len(new_password) < 8:
            return render_template("reset_password.html", form_type="reset", error="Password must be at least 8 characters long.")

        # Update the user's password in the database
        conn = get_db()
        cur = conn.cursor()
        hashed_password = generate_password_hash(new_password)
        cur.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
        conn.commit()
        conn.close()

        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", form_type="reset")