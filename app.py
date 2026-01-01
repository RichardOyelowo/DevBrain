import sqlite3
from flask_session import Session
from auth import login_required, get_db, auth, mail
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

# configure mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD

mail.init_app(app) # to configure the mail config to auth.py Mail instance

# Registering auth routes
csrf.exempt(auth)  # Exempt auth routes from CSRF protection since it's pre-login
app.register_blueprint(auth)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/quiz", methods=["GET", "POST"])
@csrf.exempt
def quiz():
    if request.method == "POST":
        score = request.form.get("score")
        question_count = request.form.get("question_count")
        
        if score and question_count:
            score = int(score)
            question_count = int(question_count)
            
            # passes blank list/dict if none was found to prevent error
            questions = session.get("questions", [])
            limit = session.get("quiz_data", {}).get("limit", 10)
            
            # Check if quiz is complete to grade and store infos
            if question_count >= limit or question_count >= len(questions):
                percentage = (score / limit) * 100
                
                # Grading Levels
                if percentage < 40:
                    grade = "Needs Improvement"
                elif percentage < 60:
                    grade = "Fair"
                elif percentage < 75:
                    grade = "Average"
                elif percentage < 90:
                    grade = "Competent"
                else:
                    grade = "Mastery"
                
                # Saves data for users with acct
                if "user_id" in session:
                    conn = get_db()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO quizzes (user_id, topic, difficulty, question_count, score, grade) "
                        "VALUES (?, ?, ?, ?, ?, ?)", 
                        (session["user_id"], session["quiz_data"]["topic"], 
                         session["quiz_data"]["difficulty"].upper(), limit, score, grade)
                    )
                    conn.commit()
                    conn.close()
                
                # Removes rendered/answered questions
                session.pop("questions", None)
                session.pop("quiz_data", None)
                
                return render_template("results.html", score=score, total=limit, grade=grade, percentage=round(percentage, 2))
            
            # Load next question is safe because we checked if it's done
            next_question = questions[question_count]
            next_question["score"] = score
            next_question["question_count"] = question_count
            
            return render_template("quiz.html", data=next_question, answers=next_question.get("answers", []))
        
        else:
            user_data = { 
                "topic": "&".join(request.form.getlist("topics")) or None,
                "difficulty": request.form.get("difficulty") or None,
                "limit": int(request.form.get("limit")) if request.form.get("limit") else None
            }

            questions = brain.get_questions(**{k: v for k, v in user_data.items() if v is not None})
            
            if not isinstance(questions, list) or len(questions) == 0:
                topics = brain.DEFAULT_TOPICS
                return render_template("quiz.html", error="No questions found for the selected criteria.", topics=topics)

            session["questions"] = questions
            
            defaults = {"topic": "uncategorized", "limit": 10, "difficulty": "Easy"}
            session["quiz_data"] = {**defaults, **{k: v for k, v in user_data.items() if v is not None}}
            questions[0]["score"] = 0
            questions[0]["question_count"] = 0

            return render_template("quiz.html", data=questions[0], answers=questions[0].get("answers", []))

    topics = brain.DEFAULT_TOPICS
    return render_template("quiz.html", topics=topics)


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

print(brain.fetch_quiz_topics())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)