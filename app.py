import sqlite3
from flask_session import Session
from auth import login_required, get_db, auth
from config import SECRET_KEY, DATABASE_URL, EMAIL, EMAIL_PASSWORD
from flask import Flask, request, render_template, redirect, url_for, session
from flask_wtf import CSRFProtect
import smtplib
from question import Questions

app = Flask(__name__)
csrf = CSRFProtect(app)

# Configure session to use filesystem (instead of signed cookies)
app.secret_key = SECRET_KEY
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

brain = Questions() # Questions class instance

conn = get_db() #connection
cur = conn.cursor() #cursor 

# Registering auth routes
app.register_blueprint(auth)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods= ["GET", "POST"])
@login_required
def index():
    session["topics"] = brain.fetch_quiz_topics()
    return render_template("index.html", topics=session["topics"])


@app.route("/quiz", methods= ["POST"])
@login_required
def quiz():
    if request.method != "POST":
        return redirect(url_for("index"))

    data = brain.get_questions(topic= request.form.get("quiz[topics][]"), 
                               limit= int(request.form.get("quiz[limit]")),
                               difficulty= request.form.get("quiz[difficulty]"))
                               

    session['quiz_data'] = data

    return render_template("quiz.html", data=session['quiz_data'])


@app.route("/result", methods= ["POST"])
@login_required
def result():
    render_template("results.html")


@app.route("/history", methods=["GET"])
@login_required
def history():
    render_template("history.html")


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)