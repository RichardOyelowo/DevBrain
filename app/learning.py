from collections import Counter, defaultdict
from datetime import datetime, timedelta
import random
import re

from sqlalchemy import func

from .extensions import db
from .models import (
    AnswerOption,
    Language,
    LegacyQuiz,
    Question,
    QuestionImportBatch,
    QuizAttempt,
    QuizAttemptAnswer,
    QuizPreset,
    Topic,
)
from .utils import calculate_grade


DIFFICULTIES = ("EASY", "MEDIUM", "HARD")
FREE_WEEKLY_QUIZ_LIMIT = 5
PRESET_ACCENTS = ("mint", "amber", "red", "blue", "violet")
DEPRECATED_TOPIC_SLUGS = {"python", "javascript", "sql", "http"}


def slugify(value):
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "topic"


def normalize_difficulty(value):
    value = (value or "EASY").strip().upper()
    return value if value in DIFFICULTIES else "EASY"


def get_active_topics():
    return (
        Topic.query.filter(Topic.is_active.is_(True), ~Topic.slug.in_(DEPRECATED_TOPIC_SLUGS))
        .order_by(Topic.name)
        .all()
    )


def get_available_languages():
    languages = Language.query.filter_by(is_active=True).order_by(Language.name).all()
    if languages:
        return languages

    rows = (
        db.session.query(Question.language)
        .filter(
            Question.status == "published",
            Question.is_archived.is_(False),
            Question.language.isnot(None),
            Question.language != "",
        )
        .distinct()
        .order_by(Question.language)
        .all()
    )
    return [
        type("LanguageOption", (), {"name": row[0].title(), "slug": row[0], "description": ""})()
        for row in rows
    ]


def get_quiz_presets():
    presets = (
        QuizPreset.query.join(Topic)
        .filter(QuizPreset.is_active.is_(True), Topic.is_active.is_(True))
        .order_by(QuizPreset.position, QuizPreset.title)
        .all()
    )
    return [
        {
            "id": preset.id,
            "slug": preset.slug,
            "topic_id": preset.topic_id,
            "topic_name": preset.topic.name,
            "title": preset.title,
            "description": preset.description,
            "difficulty": preset.difficulty,
            "limit": preset.question_limit,
            "language": preset.language or "",
            "accent": preset.accent,
        }
        for preset in presets
    ]


def quiz_quota_status(user_id):
    from .models import User

    user = db.session.get(User, user_id)
    if user and user.role == "admin":
        return {
            "limit": None,
            "used": 0,
            "remaining": None,
            "is_unlimited": True,
        }

    window_start = datetime.utcnow() - timedelta(days=7)
    used = QuizAttempt.query.filter(
        QuizAttempt.user_id == user_id,
        QuizAttempt.created_at >= window_start,
    ).count()
    return {
        "limit": FREE_WEEKLY_QUIZ_LIMIT,
        "used": used,
        "remaining": max(FREE_WEEKLY_QUIZ_LIMIT - used, 0),
        "is_unlimited": False,
    }


def can_start_quiz(user_id):
    quota = quiz_quota_status(user_id)
    return quota["is_unlimited"] or quota["remaining"] > 0


def normalize_language(value):
    return (value or "").strip().lower()


def select_questions(topic_ids=None, difficulty=None, limit=10, language=None):
    selected = []
    seen_ids = set()
    language = normalize_language(language)

    def collect(query):
        questions = query.all()
        random.shuffle(questions)
        for question in questions:
            if question.id in seen_ids or len(selected) >= limit:
                continue
            selected.append(question)
            seen_ids.add(question.id)

    base = Question.query.join(Topic).filter(
        Question.status == "published",
        Question.is_archived.is_(False),
        Topic.is_active.is_(True),
    )
    if topic_ids:
        topic_base = base.filter(Question.topic_id.in_(topic_ids))
        if language and difficulty:
            collect(topic_base.filter(Question.difficulty == normalize_difficulty(difficulty), func.lower(Question.language) == language))
        if language:
            collect(topic_base.filter(func.lower(Question.language) == language))
        if difficulty:
            collect(topic_base.filter(Question.difficulty == normalize_difficulty(difficulty)))
        collect(topic_base)

    if len(selected) < limit and language and difficulty:
        collect(base.filter(Question.difficulty == normalize_difficulty(difficulty), func.lower(Question.language) == language))

    if len(selected) < limit and language:
        collect(base.filter(func.lower(Question.language) == language))

    if len(selected) < limit and difficulty:
        collect(base.filter(Question.difficulty == normalize_difficulty(difficulty)))

    if len(selected) < limit:
        collect(base)

    return selected[:limit]


def create_attempt(user_id, topic_ids, difficulty, limit, language=None):
    difficulty = normalize_difficulty(difficulty)
    language = normalize_language(language)
    questions = select_questions(topic_ids, difficulty, limit, language)
    if not questions and difficulty:
        questions = select_questions(topic_ids, None, limit, language)
    if not questions:
        return None

    topic_names = sorted({question.topic.name for question in questions})
    attempt = QuizAttempt(
        user_id=user_id,
        topic_id=questions[0].topic_id if len(topic_names) == 1 else None,
        topic_label=", ".join(topic_names),
        difficulty=difficulty,
        question_count=len(questions),
        status="in_progress",
    )
    db.session.add(attempt)
    db.session.flush()

    for position, question in enumerate(questions, start=1):
        db.session.add(
            QuizAttemptAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                position=position,
            )
        )
    db.session.commit()
    return attempt


def get_next_pending_answer(attempt):
    return next((answer for answer in attempt.answers if not answer.selected_option_id), None)


def submit_answer(attempt, answer_id, option_id):
    attempt_answer = QuizAttemptAnswer.query.filter_by(
        id=answer_id,
        attempt_id=attempt.id,
    ).first_or_404()
    if attempt_answer.selected_option_id:
        return attempt_answer

    option = AnswerOption.query.filter_by(
        id=option_id,
        question_id=attempt_answer.question_id,
    ).first_or_404()

    attempt_answer.selected_option_id = option.id
    attempt_answer.is_correct = option.is_correct
    attempt_answer.answered_at = datetime.utcnow()

    if option.is_correct:
        attempt.score += 1

    if attempt.answered_count >= attempt.question_count:
        grade, _ = calculate_grade(attempt.score, attempt.question_count)
        attempt.grade = grade
        attempt.status = "completed"
        attempt.completed_at = datetime.utcnow()
        _write_legacy_summary(attempt)

    db.session.commit()
    return attempt_answer


def _write_legacy_summary(attempt):
    if not attempt.user_id:
        return
    existing = LegacyQuiz.query.filter_by(
        user_id=attempt.user_id,
        date=attempt.created_at,
        topic=attempt.topic_label,
    ).first()
    if existing:
        return
    db.session.add(
        LegacyQuiz(
            user_id=attempt.user_id,
            date=attempt.completed_at or datetime.utcnow(),
            topic=attempt.topic_label,
            difficulty=attempt.difficulty,
            question_count=attempt.question_count,
            score=attempt.score,
            grade=attempt.grade,
        )
    )


def dashboard_stats(user_id):
    attempts = QuizAttempt.query.filter_by(user_id=user_id, status="completed").order_by(
        QuizAttempt.completed_at.desc()
    ).all()
    if not attempts:
        legacy = LegacyQuiz.query.filter_by(user_id=user_id).order_by(LegacyQuiz.date.desc()).all()
        return _legacy_dashboard_stats(legacy)

    total = len(attempts)
    avg_score = round(sum(attempt.percentage for attempt in attempts) / total, 1)
    topic_scores = defaultdict(list)
    for attempt in attempts:
        topic_scores[attempt.topic_label].append(attempt.percentage)

    ranked = sorted(
        ((topic, sum(scores) / len(scores)) for topic, scores in topic_scores.items()),
        key=lambda item: item[1],
    )
    recent = attempts[:5]

    return {
        "total": total,
        "average": avg_score,
        "strongest": ranked[-1][0] if ranked else "Not enough data",
        "weakest": ranked[0][0] if ranked else "Not enough data",
        "recent": recent,
        "recommended": ranked[0][0] if ranked else _default_topic_name(),
    }


def _legacy_dashboard_stats(rows):
    if not rows:
        return {
            "total": 0,
            "average": 0,
            "strongest": "No attempts yet",
            "weakest": "No attempts yet",
            "recent": [],
            "recommended": _default_topic_name(),
        }
    percentages = [(row.score / row.question_count) * 100 for row in rows if row.question_count]
    topic_counts = Counter(row.topic for row in rows)
    return {
        "total": len(rows),
        "average": round(sum(percentages) / len(percentages), 1) if percentages else 0,
        "strongest": topic_counts.most_common(1)[0][0],
        "weakest": topic_counts.most_common()[-1][0],
        "recent": rows[:5],
        "recommended": topic_counts.most_common()[-1][0],
    }


def _default_topic_name():
    topic = Topic.query.filter_by(is_active=True).order_by(Topic.name).first()
    return topic.name if topic else "Data Structures"


def upsert_topic(name, description="", is_active=True, topic_id=None):
    name = (name or "").strip()
    if not name:
        raise ValueError("Topic name is required.")
    slug = slugify(name)
    topic = db.session.get(Topic, int(topic_id)) if topic_id else Topic.query.filter_by(slug=slug).first()
    if not topic:
        topic = Topic(name=name, slug=slug)
        db.session.add(topic)
    topic.name = name
    topic.slug = slug
    topic.description = description or ""
    topic.is_active = is_active
    db.session.commit()
    return topic


def upsert_language(name, description="", is_active=True, language_id=None):
    name = (name or "").strip()
    if not name:
        raise ValueError("Language name is required.")
    slug = normalize_language(name)
    language = db.session.get(Language, int(language_id)) if language_id else Language.query.filter_by(slug=slug).first()
    if not language:
        language = Language(name=name, slug=slug)
        db.session.add(language)
    language.name = name
    language.slug = slug
    language.description = description or ""
    language.is_active = is_active
    db.session.commit()
    return language


def delete_topic(topic_id):
    topic = db.session.get(Topic, int(topic_id))
    if not topic:
        raise ValueError("Category was not found.")

    if topic.questions or QuizPreset.query.filter_by(topic_id=topic.id).first():
        topic.is_active = False
        db.session.commit()
        return "Category has linked content, so it was deactivated instead of permanently deleted."

    db.session.delete(topic)
    db.session.commit()
    return "Category deleted."


def delete_language(language_id):
    language = db.session.get(Language, int(language_id))
    if not language:
        raise ValueError("Language was not found.")

    db.session.delete(language)
    db.session.commit()
    return "Language deleted."


def upsert_quiz_preset(form):
    preset_id = form.get("preset_id")
    preset = db.session.get(QuizPreset, int(preset_id)) if preset_id else None
    title = (form.get("title") or "").strip()
    if not title:
        raise ValueError("Preset title is required.")

    if preset is None:
        preset = QuizPreset(slug=slugify(title))
        db.session.add(preset)

    preset.topic_id = int(form.get("topic_id"))
    preset.title = title
    preset.slug = slugify(form.get("slug") or title)
    preset.description = (form.get("description") or "").strip()
    preset.difficulty = normalize_difficulty(form.get("difficulty"))
    preset.question_limit = min(max(int(form.get("question_limit") or 5), 1), 25)
    preset.language = normalize_language(form.get("language")) or None
    preset.accent = form.get("accent") if form.get("accent") in PRESET_ACCENTS else "mint"
    preset.position = int(form.get("position") or 0)
    preset.is_active = bool(form.get("is_active"))
    db.session.commit()
    return preset


def save_question_from_form(form, question=None, source="manual"):
    if question is None:
        question = Question(source=source)
        db.session.add(question)

    question.topic_id = int(form.get("topic_id"))
    question.prompt = form.get("prompt", "").strip()
    if not question.prompt:
        raise ValueError("Question prompt is required.")
    question.description = form.get("description", "").strip()
    question.explanation = form.get("explanation", "").strip()
    question.difficulty = normalize_difficulty(form.get("difficulty"))
    question.status = form.get("status", "draft")
    question.language = normalize_language(form.get("language")) or None
    question.code_snippet = form.get("code_snippet", "").strip() or None
    question.is_archived = bool(form.get("is_archived"))

    db.session.flush()
    AnswerOption.query.filter_by(question_id=question.id).delete()
    correct_index = int(form.get("correct_option", "0"))
    option_texts = form.getlist("options")
    for index, text in enumerate(option_texts):
        text = text.strip()
        if not text:
            continue
        db.session.add(
            AnswerOption(
                question_id=question.id,
                text=text,
                is_correct=index == correct_index,
                position=index,
            )
        )
    db.session.commit()
    return question


def import_questions_from_payload(user_id, payload):
    items = _extract_import_items(payload)
    prepared = [_validate_import_item(item, index) for index, item in enumerate(items, start=1)]

    batch = QuestionImportBatch(user_id=user_id, count=len(prepared), status="completed")
    db.session.add(batch)

    for item in prepared:
        topic = _resolve_import_topic(item)
        question = Question(
            topic=topic,
            prompt=item["prompt"],
            description=item["description"],
            explanation=item["explanation"],
            difficulty=item["difficulty"],
            status="draft",
            is_archived=False,
            language=item["language"],
            code_snippet=item["code_snippet"],
            source="import",
        )
        db.session.add(question)
        db.session.flush()

        for position, option in enumerate(item["options"]):
            db.session.add(
                AnswerOption(
                    question_id=question.id,
                    text=option["text"],
                    is_correct=option["is_correct"],
                    position=position,
                )
            )

    db.session.commit()
    return batch


def _extract_import_items(payload):
    if isinstance(payload, dict):
        payload = payload.get("questions")
    if not isinstance(payload, list):
        raise ValueError('Import payload must be a JSON list or an object with a "questions" list.')
    if not payload:
        raise ValueError("Import payload must include at least one question.")
    if len(payload) > 100:
        raise ValueError("Import batches are limited to 100 questions at a time.")
    return payload


def _validate_import_item(item, index):
    if not isinstance(item, dict):
        raise ValueError(f"Question {index} must be a JSON object.")

    prompt = _required_text(item, "prompt", index)
    topic_name = (item.get("topic") or item.get("topic_name") or "").strip()
    topic_id = item.get("topic_id")
    if topic_id not in (None, ""):
        try:
            topic_id = int(topic_id)
        except (TypeError, ValueError):
            raise ValueError(f"Question {index} has an invalid topic_id.")
    if not topic_name and not topic_id:
        raise ValueError(f"Question {index} must include topic or topic_id.")

    raw_options = item.get("options")
    if not isinstance(raw_options, list) or len(raw_options) < 2:
        raise ValueError(f"Question {index} must include at least two options.")

    options = _normalize_import_options(raw_options, item, index)
    if sum(1 for option in options if option["is_correct"]) != 1:
        raise ValueError(f"Question {index} must have exactly one correct option.")

    return {
        "topic_id": topic_id,
        "topic": topic_name,
        "topic_description": (item.get("topic_description") or "").strip(),
        "prompt": prompt,
        "description": (item.get("description") or item.get("description_text") or "").strip(),
        "explanation": (item.get("explanation") or "").strip(),
        "difficulty": normalize_difficulty(item.get("difficulty")),
        "language": normalize_language(item.get("language")) or None,
        "code_snippet": (item.get("code_snippet") or item.get("code") or "").strip() or None,
        "options": options,
    }


def _required_text(item, key, index):
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Question {index} must include {key}.")
    return value.strip()


def _normalize_import_options(raw_options, item, question_index):
    correct_answer = item.get("correct_answer")
    correct_index = item.get("correct_option")
    if correct_index not in (None, ""):
        try:
            correct_index = int(correct_index)
        except (TypeError, ValueError):
            raise ValueError(f"Question {question_index} has an invalid correct_option.")
    options = []

    for option_index, raw_option in enumerate(raw_options):
        if isinstance(raw_option, str):
            text = raw_option.strip()
            is_correct = text == correct_answer or option_index == correct_index
        elif isinstance(raw_option, dict):
            text = (raw_option.get("text") or raw_option.get("answer") or "").strip()
            is_correct = bool(raw_option.get("is_correct", raw_option.get("correct", False)))
            if correct_answer:
                is_correct = text == correct_answer
            if correct_index is not None:
                is_correct = option_index == correct_index
        else:
            raise ValueError(f"Question {question_index} option {option_index + 1} must be text or an object.")

        if not text:
            raise ValueError(f"Question {question_index} option {option_index + 1} must include text.")
        options.append({"text": text, "is_correct": is_correct})

    return options


def _resolve_import_topic(item):
    if item["topic_id"]:
        topic = db.session.get(Topic, item["topic_id"])
        if not topic:
            raise ValueError(f"Topic id {item['topic_id']} does not exist.")
        return topic

    slug = slugify(item["topic"])
    topic = Topic.query.filter_by(slug=slug).first()
    if topic:
        return topic

    topic = Topic(
        name=item["topic"],
        slug=slug,
        description=item["topic_description"],
        is_active=True,
    )
    db.session.add(topic)
    db.session.flush()
    return topic
