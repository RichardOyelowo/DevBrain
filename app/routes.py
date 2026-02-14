from flask import Blueprint, render_template, request, session, redirect, url_for, current_app
from .utils import calculate_grade, save_quiz_result
from .extensions import csrf, login_required
from .db import get_db
from .question import Questions


main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@main.route("/quiz", methods=["GET", "POST"])
@csrf.exempt
def quiz():
    brain = Questions(current_app.config["API_KEY"])

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

@main.route("/history", methods=["GET"])
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


@main.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


