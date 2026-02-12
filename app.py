from flask import Flask, request, render_template, redirect, url_for, session
from utils import calculate_grade, save_quiz_result
from config import SECRET_KEY, DATABASE_URL
from auth import login_required, get_db, auth, mail
from flask_wtf import CSRFProtect
from datetime import timedelta
from question import Questions
import smtplib
import sqlite3
import redis
import os


app = Flask(__name__)
csrf = CSRFProtect(app)

app.secret_key = SECRET_KEY

# Session config
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,
)

brain = Questions() # Questions class instance

# ---------------- Reset Email Utility ----------------
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

mail = Mail()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Registering auth routes
app.register_blueprint(auth)

csrf.exempt(auth)

init_db()


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


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
            if selected == current.get("correct_answer"):
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
                # clear current quiz data
                for key in ("questions", "quiz_index", "quiz_score", "quiz_data"):
                    session.pop(key, None)

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
            print(user_data)

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


if __name__=="__main__":
    app.run(debug=True)

