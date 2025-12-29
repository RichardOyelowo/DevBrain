import sqlite3
from flask import session, request,render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import DATABASE_URL


def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    
    return conn


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

        conn = get_db()
        cur = conn.cursor()

        # Check if username already exists
        existing = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if existing is not None:
            conn.close() # Close the database connection
            return render_template("register.html", error="Username already exists")

        # Insert new user into the database
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, generate_password_hash(password)))
        conn.commit()

        row = cur.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        conn.close() # Close the database connection

        session["user_id"] = row["id"]

        return redirect(url_for("index"))

    return render_template("register.html")


def login():

    session.clear() # forget previous user

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", error="Fill all details")

        conn = get_db()
        cur = conn.cursor()

        row = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close() # Close the database connection

        if row is None or not check_password_hash(row["password"], password):
            return render_template("login.html", error="Invalid username or password")

        session["user_id"] = row["id"]

        return redirect(url_for("index"))

    return render_template("login.html", error=None)


def logout():
    # clear user session
    session.clear()

    return redirect("/")