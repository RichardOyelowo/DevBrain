import sqlite3
from flask_session import Session
from flask import Flask, request, render_template, redirect, url_for, session
from question import Questions
from auth import register, login, logout
from config import SECRET_KEY, DATABASE_URL

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.secret_key = SECRET_KEY
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize question handler
brain = Questions()
# Initialize database connection
db = sqlite3.connect(DATABASE_URL, check_same_thread=False)
db = db.cursor()

# Registering auth routes
app.add_url_rule("/register", view_func=register, methods=["GET", "POST"])
app.add_url_rule("/login", view_func=login, methods=["GET", "POST"])
app.add_url_rule("/logout", view_func=logout)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods= ["GET", "POST"])
def index():
    session["topics"] = brain.fetch_quiz_topics()
    return render_template("index.html", topics=session["topics"])


@app.route("/quiz", methods= ["POST"])
def quiz():
    if request.method != "POST":
        return redirect(url_for("index"))

    data = brain.get_questions(topic= request.form.get("quiz[topics][]"), 
                               limit= int(request.form.get("quiz[limit]")),
                               difficulty= request.form.get("quiz[difficulty]"))
                               

    session['quiz_data'] = data

    return render_template("quiz.html", data=session['quiz_data'])


@app.route("/result", methods= ["POST"])
def result():
    render_template("results.html")


@app.route("/history", methods=["GET"])
def history():
    render_template("history.html")


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
