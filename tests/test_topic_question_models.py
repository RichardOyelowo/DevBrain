from app.extensions import db
from app.db import ensure_starter_catalog
from app.learning import get_active_topics, save_question_from_form, slugify
from app.models import AnswerOption, Language, Question, QuizPreset, Topic
from tests.base import DevBrainTestCase


class TopicModelTest(DevBrainTestCase):
    def test_seed_bank_creates_active_topics(self):
        topics = get_active_topics()

        self.assertGreaterEqual(len(topics), 1)
        self.assertTrue(all(topic.is_active for topic in topics))

    def test_slugify_normalizes_topic_names(self):
        self.assertEqual(slugify("Backend Architecture!"), "backend-architecture")
        self.assertEqual(slugify("  SQL & Data  "), "sql-data")

    def test_topic_questions_relationship_orders_seed_questions(self):
        topic = Topic.query.filter_by(name="Data Structures").first()

        self.assertIsNotNone(topic)
        self.assertGreaterEqual(len(topic.questions), 1)

    def test_seed_bank_creates_framework_topics(self):
        topic_names = {topic.name for topic in get_active_topics()}

        self.assertTrue({"React", "Next.js", "Django", "Flask", "Laravel", "Express"}.issubset(topic_names))

    def test_language_names_are_not_active_topics(self):
        topic_names = {topic.name for topic in get_active_topics()}

        self.assertFalse({"Python", "JavaScript", "SQL"}.intersection(topic_names))

    def test_seed_bank_creates_language_filters(self):
        language_slugs = {language.slug for language in Language.query.filter_by(is_active=True).all()}

        self.assertTrue({"python", "javascript", "typescript", "sql", "php", "go", "rust", "shell"}.issubset(language_slugs))

    def test_seed_bank_creates_editable_quiz_presets(self):
        self.assertGreaterEqual(QuizPreset.query.filter_by(is_active=True).count(), 4)

    def test_startup_catalog_command_seeds_empty_database(self):
        db.drop_all()
        db.create_all()

        seeded = ensure_starter_catalog()

        self.assertTrue(seeded)
        self.assertGreaterEqual(Topic.query.filter_by(is_active=True).count(), 20)
        self.assertGreaterEqual(Language.query.filter_by(is_active=True).count(), 10)
        self.assertGreaterEqual(QuizPreset.query.filter_by(is_active=True).count(), 4)
        self.assertGreaterEqual(Question.query.filter_by(source="seed").count(), 1)


class QuestionModelTest(DevBrainTestCase):
    def test_seed_bank_creates_published_questions(self):
        self.assertGreaterEqual(Question.query.filter_by(status="published").count(), 1)

    def test_correct_option_returns_the_correct_answer_option(self):
        question = Question.query.filter(Question.options.any(AnswerOption.is_correct.is_(True))).first()

        self.assertIsNotNone(question.correct_option)
        self.assertTrue(question.correct_option.is_correct)

    def test_save_question_from_form_creates_options(self):
        topic = Topic.query.first()
        form_data = {
            "topic_id": str(topic.id),
            "prompt": "Which layer stores DevBrain questions?",
            "description": "Choose the persistence layer.",
            "explanation": "Questions are stored in database tables.",
            "difficulty": "EASY",
            "status": "published",
            "language": "",
            "code_snippet": "",
            "correct_option": "1",
            "options": ["Redis only", "Database", "Template files", "Browser storage"],
        }

        question = save_question_from_form(_FakeForm(form_data))

        self.assertEqual(len(question.options), 4)
        self.assertEqual(question.correct_option.text, "Database")

    def test_blank_prompt_is_rejected(self):
        topic = Topic.query.first()
        form_data = {
            "topic_id": str(topic.id),
            "prompt": "",
            "difficulty": "EASY",
            "status": "draft",
            "correct_option": "0",
            "options": ["A", "B"],
        }

        with self.assertRaises(ValueError):
            save_question_from_form(_FakeForm(form_data))


class _FakeForm(dict):
    def getlist(self, key):
        value = self.get(key, [])
        return value if isinstance(value, list) else [value]
