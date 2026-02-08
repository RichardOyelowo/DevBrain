from flask import Flask, request, render_template, redirect, url_for, session
from config import SECRET_KEY, DATABASE_URL, EMAIL, EMAIL_PASSWORD
from auth import login_required, get_db, auth, mail
from flask_wtf import CSRFProtect
from flask_session import Session
from question import Questions
from datetime import timedelta
import sqlite3
import smtplib
import redis
import os

# database
DATABASE_PATH = DATABASE_URL

app = Flask(__name__)
csrf = CSRFProtect(app)

app.secret_key = SECRET_KEY
app.config["SESSION_TYPE"] = "redis" 
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "quizapp:"

try:
    r = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
    app.config["SESSION_REDIS"] = r
except redis.exceptions.ConnectionError:
    print("Redis not available. Sessions may not persist.")

Session(app)

brain = Questions() # Questions class instance

# configure mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD

mail.init_app(app) # to configure the mail config to auth.py Mail instance

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Registering auth routes
csrf.exempt(auth.login)
csrf.exempt(auth.register)

app.register_blueprint(auth)

def init_db():
    if not os.path.exists(DATABASE_PATH):
        with sqlite3.connect(DATABASE_PATH) as conn:
            with open("schema.sql", "r") as f:
                conn.executescript(f.read())

init_db()


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


def calculate_grade(score, total):
    """Calculate grade based on percentage score"""
    percentage = (score / total) * 100
    
    if percentage < 40:
        return "Needs Improvement", percentage
    elif percentage < 60:
        return "Fair", percentage
    elif percentage < 75:
        return "Average", percentage
    elif percentage < 90:
        return "Competent", percentage
    else:
        return "Mastery", percentage

def save_quiz_result(user_id, topic, difficulty, limit, score, grade):
    """Save quiz results to database for logged-in users"""
    conn = get_db()
    cur = conn.cursor()
    
    #for multiple topics combined
    if "&" in topic:
        topic = topic.replace("&", ", ")

    cur.execute("INSERT INTO quizzes (user_id, topic, difficulty, question_count, score, grade) VALUES (?, ?, ?, ?, ?, ?)", 
        (user_id, topic, difficulty.upper(), limit, score, grade))
    conn.commit()
    conn.close()

def clear_quiz_session():
    session.pop("questions", None)
    session.pop("quiz_index", None)
    session.pop("quiz_score", None)
    session.pop("quiz_data", None)


@app.route("/quiz", methods=["GET", "POST"])
@csrf.exempt
def quiz():
    if request.method == "POST":

        # 1️⃣ Answer submission
        if "answer" in request.form:
            selected = request.form.get("answer")

            questions = session.get("questions", [])
            index = session.get("quiz_index", 0)
            score = session.get("quiz_score", 0)
            limit = session.get("quiz_data", {}).get("limit", 10)

            if index >= len(questions):
                return redirect(url_for("quiz"))

            current = questions[index]

            # ✅ server decides correctness
            if selected == current.get("correct"):
                score += 1

            index += 1

            # save updated state
            session["quiz_index"] = index
            session["quiz_score"] = score

            # 2️⃣ Quiz finished
            if index >= limit or index >= len(questions):
                grade, percentage = calculate_grade(score, limit)

                if "user_id" in session:
                    save_quiz_result(
                        session["user_id"],
                        session["quiz_data"]["topic"],
                        session["quiz_data"]["difficulty"],
                        limit,
                        score,
                        grade
                    )

                clear_quiz_session()

                return render_template(
                    "results.html",
                    score=score,
                    total=limit,
                    grade=grade,
                    percentage=round(percentage, 2)
                )

            # 3️⃣ Next question
            next_question = questions[index]
            return render_template(
                "quiz.html",
                data=next_question,
                answers=next_question.get("answers", [])
            )

        # 4️⃣ Quiz setup
        else:
            user_data = {
                "topic": "&".join(request.form.getlist("topics")) or None,
                "difficulty": request.form.get("difficulty") or None,
                "limit": int(request.form.get("limit")) if request.form.get("limit") else 10
            }

            questions = brain.get_questions(
                **{k: v for k, v in user_data.items() if v is not None}
            )

            if not questions:
                return render_template(
                    "quiz.html",
                    error="No questions found.",
                    topics=brain.DEFAULT_TOPICS
                )

            session["questions"] = questions
            session["quiz_index"] = 0
            session["quiz_score"] = 0
            session["quiz_data"] = {
                "topic": user_data["topic"] or "uncategorized",
                "difficulty": user_data["difficulty"] or "Easy",
                "limit": user_data["limit"]
            }

            first = questions[0]
            return render_template(
                "quiz.html",
                data=first,
                answers=first.get("answers", [])
            )

    # GET request
    return render_template("quiz.html", topics=brain.DEFAULT_TOPICS)


@app.route("/history", methods=["GET"])
@login_required
def history():
    conn = get_db()
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT * FROM quizzes "
        "WHERE user_id = ? ORDER BY date DESC", 
        (session["user_id"],)
    ).fetchall()
    conn.close()
    
    history = []
    if rows:
        for row in rows:
            history.append({
                "date": row["date"],
                "topic": row["topic"],
                "difficulty": row["difficulty"],
                "question_count": row["question_count"],
                "score": row["score"],
                "grade": row["grade"]
            })
    

    return render_template("history.html", history=history)


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

