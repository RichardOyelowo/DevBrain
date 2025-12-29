import sqlite3
from flask import session, request,render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import DATABASE_URL

db = sqlite3.connect(DATABASE_URL, check_same_thread=False)
db= db.cursor()


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return render_template("register.html", error="Fill all details")

        if password != confirmation:
            return render_template("register.html", error="Passwords do not match")

        # Check if username already exists
        existing = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(existing) != 0:
            return render_template("register.html", error="Username already exists")

        # Insert new user into the database
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, generate_password_hash(password))
        db.commit()

        rows = db.execute("SELECT id FROM users WHERE username = ?", username)

        session["user_id"] = rows[0]["id"]

        return redirect(url_for("index"))

    return render_template("register.html")


def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", error="Fill all details")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return render_template("login.html", error="Invalid username or password")

        session["user_id"] = rows[0]["id"]

    return redirect(url_for("index"))


def logout():
    # clear user session
    session.clear()

    return redirect("/")