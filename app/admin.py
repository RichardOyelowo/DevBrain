import json

from flask import Blueprint, abort, flash, render_template, request, redirect, session, url_for

from .extensions import admin_required, csrf, db
from .learning import (
    delete_language,
    delete_topic,
    DEPRECATED_TOPIC_SLUGS,
    DIFFICULTIES,
    get_active_topics,
    get_available_languages,
    import_questions_from_payload,
    save_question_from_form,
    upsert_language,
    upsert_quiz_preset,
    upsert_topic,
    PRESET_ACCENTS,
)
from .models import Language, Question, QuestionImportBatch, QuizPreset, Topic


admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("")
@admin.route("/")
@admin_required
def home():
    stats = {
        "topics": Topic.query.count(),
        "languages": Language.query.count(),
        "presets": QuizPreset.query.count(),
        "published": Question.query.filter_by(status="published", is_archived=False).count(),
        "drafts": Question.query.filter_by(status="draft", is_archived=False).count(),
        "imports": QuestionImportBatch.query.count(),
    }
    return render_template("admin/index.html", stats=stats)


@admin.route("/questions")
@admin_required
def questions():
    questions = Question.query.order_by(Question.updated_at.desc()).all()
    return render_template("admin/questions.html", questions=questions)


@admin.route("/questions/new", methods=["GET", "POST"])
@csrf.exempt
@admin_required
def question_new():
    if request.method == "POST":
        try:
            question = save_question_from_form(request.form)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("admin.question_new"))
        flash("Question saved.", "success")
        return redirect(url_for("admin.question_edit", question_id=question.id))
    return render_template("admin/question_form.html", question=None, topics=get_active_topics(), languages=get_available_languages())


@admin.route("/questions/<int:question_id>/edit", methods=["GET", "POST"])
@csrf.exempt
@admin_required
def question_edit(question_id):
    question = db.session.get(Question, question_id) or abort(404)
    if request.method == "POST":
        try:
            save_question_from_form(request.form, question=question)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("admin.question_edit", question_id=question.id))
        flash("Question updated.", "success")
        return redirect(url_for("admin.questions"))
    return render_template("admin/question_form.html", question=question, topics=get_active_topics(), languages=get_available_languages())


@admin.route("/topics", methods=["GET", "POST"])
@csrf.exempt
@admin_required
def topics():
    if request.method == "POST":
        if request.form.get("action") == "delete":
            try:
                message = delete_topic(request.form.get("topic_id"))
            except ValueError as exc:
                flash(str(exc), "danger")
            else:
                flash(message, "success")
            return redirect(url_for("admin.topics"))

        try:
            upsert_topic(
                request.form.get("name", ""),
                request.form.get("description", ""),
                bool(request.form.get("is_active")),
                request.form.get("topic_id"),
            )
        except ValueError as exc:
            flash(str(exc), "danger")
        else:
            flash("Category saved.", "success")
        return redirect(url_for("admin.topics"))
    topics = Topic.query.filter(~Topic.slug.in_(DEPRECATED_TOPIC_SLUGS)).order_by(Topic.name).all()
    return render_template("admin/topics.html", topics=topics)


@admin.route("/languages", methods=["GET", "POST"])
@csrf.exempt
@admin_required
def languages():
    if request.method == "POST":
        if request.form.get("action") == "delete":
            try:
                message = delete_language(request.form.get("language_id"))
            except ValueError as exc:
                flash(str(exc), "danger")
            else:
                flash(message, "success")
            return redirect(url_for("admin.languages"))

        try:
            upsert_language(
                request.form.get("name", ""),
                request.form.get("description", ""),
                bool(request.form.get("is_active")),
                request.form.get("language_id"),
            )
        except ValueError as exc:
            flash(str(exc), "danger")
        else:
            flash("Language saved.", "success")
        return redirect(url_for("admin.languages"))
    languages = Language.query.order_by(Language.name).all()
    return render_template("admin/languages.html", languages=languages)


@admin.route("/presets", methods=["GET", "POST"])
@csrf.exempt
@admin_required
def presets():
    if request.method == "POST":
        try:
            upsert_quiz_preset(request.form)
        except ValueError as exc:
            flash(str(exc), "danger")
        else:
            flash("Fast start saved.", "success")
        return redirect(url_for("admin.presets"))
    presets = QuizPreset.query.order_by(QuizPreset.position, QuizPreset.title).all()
    return render_template(
        "admin/presets.html",
        presets=presets,
        topics=get_active_topics(),
        languages=get_available_languages(),
        difficulties=DIFFICULTIES,
        accents=PRESET_ACCENTS,
    )


@admin.route("/import", methods=["GET", "POST"])
@csrf.exempt
@admin_required
def import_questions():
    if request.method == "POST":
        raw_payload = request.form.get("payload", "")
        uploaded_file = request.files.get("question_file")
        if uploaded_file and uploaded_file.filename:
            raw_payload = uploaded_file.read().decode("utf-8")
        try:
            payload = json.loads(raw_payload)
            batch = import_questions_from_payload(session["user_id"], payload)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            db.session.rollback()
            flash(f"Import failed: {exc}", "danger")
            return redirect(url_for("admin.import_questions"))

        flash(f"Imported {batch.count} draft questions. Review and publish them from the question library.", "success")
        return redirect(url_for("admin.questions"))

    imports = QuestionImportBatch.query.order_by(QuestionImportBatch.created_at.desc()).all()
    return render_template("admin/import_questions.html", imports=imports)
