import sqlite3
from flask_session import Session
from auth import login_required, get_db, auth, mail
from config import SECRET_KEY, DATABASE_URL, EMAIL, EMAIL_PASSWORD
from flask import Flask, request, render_template, redirect, url_for, session
from flask_wtf import CSRFProtect
from question import Questions
import smtplib
import os

# database
DATABASE_PATH = "database.db"

def init_db():
    "creates a database if it doesn't exists"
    if not os.path.exists(DATABASE_PATH):
        with sqlite3.connect(DATABASE_PATH) as conn:
            with open("schema.sql", "r") as f:
                conn.executescript(f.read())

init_db()

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

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Registering auth routes
csrf.exempt(auth)  # Exempt auth routes from CSRF protection since it's pre-login
app.register_blueprint(auth)


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
    """Remove quiz data from session"""
    session.pop("questions", None)
    session.pop("quiz_data", None)


@app.route("/quiz", methods=["GET", "POST"])
@csrf.exempt
def quiz():
    if request.method == "POST":
        score = request.form.get("score")
        question_count = request.form.get("question_count")
        
        # Handle answer submission
        if score and question_count:
            score = int(score)
            question_count = int(question_count)
            
            questions = session.get("questions", [])
            limit = session.get("quiz_data", {}).get("limit", 10)
            
            # Check if quiz is complete
            if question_count >= limit or question_count >= len(questions):
                grade, percentage = calculate_grade(score, limit)
                
                # Save results for logged-in users
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
                return render_template("results.html", score=score, total=limit, grade=grade, percentage=round(percentage, 2))
            
            # Load next question
            next_question = questions[question_count]
            next_question["score"] = score
            next_question["question_count"] = question_count
            
            return render_template("quiz.html", data=next_question, answers=next_question.get("answers", []))
        
        # Handle quiz setup
        else:
            user_data = { 
                "topic": "&".join(request.form.getlist("topics")) or None,
                "difficulty": request.form.get("difficulty") or None,
                "limit": int(request.form.get("limit")) if request.form.get("limit") else None
            }

            questions = brain.get_questions(**{k: v for k, v in user_data.items() if v is not None})
            
            # Check if questions were found
            if not isinstance(questions, list) or len(questions) == 0:
                return render_template("quiz.html", 
                                     error="No questions found for the selected criteria.", 
                                     topics=brain.DEFAULT_TOPICS)

            # Store quiz data in session
            session["questions"] = questions
            defaults = {"topic": "uncategorized", "limit": 10, "difficulty": "Easy"}
            session["quiz_data"] = {**defaults, **{k: v for k, v in user_data.items() if v is not None}}
            
            # Set initial score and count
            questions[0]["score"] = 0
            questions[0]["question_count"] = 0

            return render_template("quiz.html", data=questions[0], 
                                 answers=questions[0].get("answers", []))

    # GET request - show topic selection
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



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)