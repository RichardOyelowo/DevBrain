from datetime import datetime

from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    attempts = db.relationship("QuizAttempt", back_populates="user", lazy="dynamic")

    @property
    def is_admin(self):
        return self.role == "admin"


class LegacyQuiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    topic = db.Column(db.String(255))
    difficulty = db.Column(db.String(20))
    question_count = db.Column(db.Integer, nullable=False, default=0)
    score = db.Column(db.Integer, nullable=False, default=0)
    grade = db.Column(db.String(40), nullable=False)


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default="")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    questions = db.relationship("Question", back_populates="topic", cascade="all, delete-orphan")


class Language(db.Model):
    __tablename__ = "languages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default="")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False, index=True)
    prompt = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, default="")
    explanation = db.Column(db.Text, default="")
    difficulty = db.Column(db.String(20), nullable=False, default="EASY", index=True)
    status = db.Column(db.String(20), nullable=False, default="draft", index=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False, index=True)
    language = db.Column(db.String(40))
    code_snippet = db.Column(db.Text)
    source = db.Column(db.String(40), default="manual")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    topic = db.relationship("Topic", back_populates="questions")
    options = db.relationship(
        "AnswerOption",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="AnswerOption.position",
    )

    @property
    def correct_option(self):
        return next((option for option in self.options if option.is_correct), None)


class QuizPreset(db.Model):
    __tablename__ = "quiz_presets"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False, index=True)
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    difficulty = db.Column(db.String(20), nullable=False, default="EASY")
    question_limit = db.Column(db.Integer, nullable=False, default=5)
    language = db.Column(db.String(40))
    accent = db.Column(db.String(40), nullable=False, default="mint")
    position = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    topic = db.relationship("Topic")


class AnswerOption(db.Model):
    __tablename__ = "answer_options"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    position = db.Column(db.Integer, default=0, nullable=False)

    question = db.relationship("Question", back_populates="options")


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=True, index=True)
    topic_label = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    question_count = db.Column(db.Integer, nullable=False, default=0)
    score = db.Column(db.Integer, nullable=False, default=0)
    grade = db.Column(db.String(40))
    status = db.Column(db.String(20), nullable=False, default="in_progress")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="attempts")
    topic = db.relationship("Topic")
    answers = db.relationship(
        "QuizAttemptAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
        order_by="QuizAttemptAnswer.position",
    )

    @property
    def answered_count(self):
        return len([answer for answer in self.answers if answer.selected_option_id])

    @property
    def percentage(self):
        if not self.question_count:
            return 0
        return round((self.score / self.question_count) * 100, 2)


class QuizAttemptAnswer(db.Model):
    __tablename__ = "quiz_attempt_answers"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempts.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False, index=True)
    selected_option_id = db.Column(db.Integer, db.ForeignKey("answer_options.id"), nullable=True)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    answered_at = db.Column(db.DateTime)

    attempt = db.relationship("QuizAttempt", back_populates="answers")
    question = db.relationship("Question")
    selected_option = db.relationship("AnswerOption", foreign_keys=[selected_option_id])


class QuestionImportBatch(db.Model):
    __tablename__ = "question_import_batches"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="completed")
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User")
