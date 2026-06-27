from flask import Blueprint, abort, flash, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from .extensions import db, login_required
from .models import QuizAttempt, User
from .forms import ChangePassword
from .learning import (
    create_attempt,
    can_start_quiz,
    dashboard_stats,
    get_active_attempt,
    get_active_topics,
    get_available_languages,
    get_next_pending_answer,
    get_quiz_presets,
    question_bank_summary,
    normalize_difficulty,
    normalize_language,
    quiz_quota_status,
    submit_answer,
    topic_availability,
)


main = Blueprint("main", __name__)


def form_int(name, default=None):
    value = request.form.get(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@main.route("/", methods=["GET", "POST"])
def index():
    if session.get("user_id"):
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main.route("/dashboard")
@login_required
def dashboard():
    stats = dashboard_stats(session["user_id"])
    quota = quiz_quota_status(session["user_id"])
    return render_template(
        "dashboard.html",
        stats=stats,
        topics=get_active_topics(),
        quota=quota,
        active_attempt=get_active_attempt(session["user_id"]),
        bank_summary=question_bank_summary(),
        topic_availability=topic_availability(),
    )


@main.route("/quiz", methods=["GET"], endpoint="quiz")
@login_required
def quiz_setup():
    quota = quiz_quota_status(session["user_id"])
    return render_template(
        "quiz_setup.html",
        topics=get_active_topics(),
        languages=get_available_languages(),
        presets=get_quiz_presets(),
        quota=quota,
        active_attempt=get_active_attempt(session["user_id"]),
        bank_summary=question_bank_summary(),
        topic_availability=topic_availability(),
    )


@main.route("/quiz/start", methods=["POST"])
@login_required
def quiz_start():
    if not can_start_quiz(session["user_id"]):
        flash("You have used your 5 free quizzes for this week. Unlimited access will be available on the paid plan.", "danger")
        return redirect(url_for("main.quiz"))

    preset_slug = request.form.get("preset")
    preset = next((item for item in get_quiz_presets() if item["slug"] == preset_slug), None)
    if preset:
        topic_ids = [preset["topic_id"]]
        difficulty = preset["difficulty"]
        limit = preset["limit"]
        language = preset["language"]
    else:
        topic_ids = [int(topic_id) for topic_id in request.form.getlist("topics") if topic_id.isdigit()]
        difficulty = normalize_difficulty(request.form.get("difficulty"))
        limit = min(max(form_int("limit", 10), 1), 25)
        language = normalize_language(request.form.get("language"))

    attempt = create_attempt(session["user_id"], topic_ids, difficulty, limit, language)
    if not attempt:
        flash("No published questions match that setup yet.", "danger")
        return redirect(url_for("main.quiz"))
    return redirect(url_for("main.quiz_question", attempt_id=attempt.id))


@main.route("/quiz/<int:attempt_id>/question", methods=["GET", "POST"])
@login_required
def quiz_question(attempt_id):
    attempt = db.session.get(QuizAttempt, attempt_id) or abort(404)
    if attempt.user_id != session.get("user_id"):
        abort(403)
    if attempt.status == "completed":
        return redirect(url_for("main.quiz_results", attempt_id=attempt.id))

    if request.method == "POST":
        answer_id = form_int("attempt_answer_id")
        option_id = form_int("option_id")
        if not answer_id or not option_id:
            flash("Choose an answer before continuing.", "danger")
            return redirect(url_for("main.quiz_question", attempt_id=attempt.id))
        submit_answer(attempt, answer_id, option_id)
        if attempt.status == "completed":
            return redirect(url_for("main.quiz_results", attempt_id=attempt.id))
        return redirect(url_for("main.quiz_question", attempt_id=attempt.id))

    pending = get_next_pending_answer(attempt)
    if not pending:
        return redirect(url_for("main.quiz_results", attempt_id=attempt.id))
    return render_template("quiz_question.html", attempt=attempt, attempt_answer=pending)


@main.route("/quiz/<int:attempt_id>/results")
@login_required
def quiz_results(attempt_id):
    attempt = db.session.get(QuizAttempt, attempt_id) or abort(404)
    if attempt.user_id != session.get("user_id"):
        abort(403)
    if attempt.status != "completed":
        return redirect(url_for("main.quiz_question", attempt_id=attempt.id))
    return render_template("results.html", attempt=attempt)


@main.route("/quiz/<int:attempt_id>/review")
@login_required
def quiz_review(attempt_id):
    attempt = db.session.get(QuizAttempt, attempt_id) or abort(404)
    if attempt.user_id != session.get("user_id"):
        abort(403)
    if attempt.status != "completed":
        return redirect(url_for("main.quiz_question", attempt_id=attempt.id))
    return render_template("review.html", attempt=attempt)


@main.route("/history", methods=["GET"])
@login_required
def history():
    topic = request.args.get("topic", "")
    difficulty = request.args.get("difficulty", "")
    query = QuizAttempt.query.filter_by(user_id=session["user_id"], status="completed")
    if topic:
        query = query.filter(QuizAttempt.topic_label.ilike(f"%{topic}%"))
    if difficulty:
        query = query.filter_by(difficulty=normalize_difficulty(difficulty))
    attempts = query.order_by(QuizAttempt.completed_at.desc()).all()
    return render_template("history.html", attempts=attempts, topics=get_active_topics())


@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = db.session.get(User, session["user_id"])
    form = ChangePassword()
    if form.validate_on_submit():
        if not check_password_hash(user.password, form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            user.password = generate_password_hash(form.password.data)
            user.password_changed_at = datetime.utcnow()
            db.session.commit()
            flash("Password updated.", "success")
            return redirect(url_for("main.profile"))
    quota = quiz_quota_status(session["user_id"])
    stats = dashboard_stats(session["user_id"])
    return render_template("profile.html", user=user, form=form, quota=quota, stats=stats)


@main.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@main.route("/pricing", methods=["GET"])
def pricing():
    return render_template("pricing.html")
