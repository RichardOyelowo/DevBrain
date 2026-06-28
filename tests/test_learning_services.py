from app.extensions import db
from app.learning import (
    can_start_quiz,
    create_attempt,
    dashboard_stats,
    get_active_attempt,
    question_bank_summary,
    QuizQuotaExceeded,
    quiz_quota_status,
    submit_answer,
    topic_availability,
)
from app.models import Language, Topic, User
from app.session_security import auth_marker
from tests.base import DevBrainTestCase


class QuizQuotaServiceTest(DevBrainTestCase):
    def test_admin_quota_is_unlimited(self):
        user = User(email="admin@example.com", password="hash", role="admin")
        db.session.add(user)
        db.session.commit()

        quota = quiz_quota_status(user.id)

        self.assertTrue(quota["is_unlimited"])
        self.assertIsNone(quota["remaining"])

    def test_free_user_quota_starts_with_five_remaining(self):
        user = User(email="learner@example.com", password="hash", role="user")
        db.session.add(user)
        db.session.commit()

        quota = quiz_quota_status(user.id)

        self.assertFalse(quota["is_unlimited"])
        self.assertEqual(quota["remaining"], 5)
        self.assertEqual(quota["plan"], "free")

    def test_pro_user_quota_starts_with_fifty_remaining(self):
        user = User(email="learner@example.com", password="hash", role="user", plan="pro")
        db.session.add(user)
        db.session.commit()

        quota = quiz_quota_status(user.id)

        self.assertFalse(quota["is_unlimited"])
        self.assertEqual(quota["limit"], 50)
        self.assertEqual(quota["remaining"], 50)
        self.assertEqual(quota["plan"], "pro")

    def test_unlimited_user_has_no_weekly_cap(self):
        user = User(email="learner@example.com", password="hash", role="user", plan="unlimited")
        db.session.add(user)
        db.session.commit()

        quota = quiz_quota_status(user.id)

        self.assertTrue(quota["is_unlimited"])
        self.assertIsNone(quota["limit"])
        self.assertIsNone(quota["remaining"])
        self.assertEqual(quota["plan"], "unlimited")

    def test_free_user_cannot_start_after_five_attempts(self):
        user = User(email="learner@example.com", password="hash", role="user")
        db.session.add(user)
        db.session.commit()
        for _ in range(5):
            create_attempt(user.id, [], "EASY", 1)

        self.assertFalse(can_start_quiz(user.id))

    def test_create_attempt_raises_when_quota_is_exhausted(self):
        user = User(email="learner@example.com", password="hash", role="user")
        db.session.add(user)
        db.session.commit()
        for _ in range(5):
            create_attempt(user.id, [], "EASY", 1)

        with self.assertRaises(QuizQuotaExceeded):
            create_attempt(user.id, [], "EASY", 1)

    def test_active_attempt_returns_latest_in_progress_attempt(self):
        user = User(email="learner@example.com", password="hash", role="user")
        db.session.add(user)
        db.session.commit()
        first = create_attempt(user.id, [], "EASY", 1)
        second = create_attempt(user.id, [], "EASY", 1)
        first.status = "completed"
        db.session.commit()

        active = get_active_attempt(user.id)

        self.assertEqual(active.id, second.id)


class LearningSignalServiceTest(DevBrainTestCase):
    def test_question_bank_summary_counts_catalog(self):
        summary = question_bank_summary()

        self.assertGreaterEqual(summary["published"], 1)
        self.assertGreaterEqual(summary["topics"], 20)
        self.assertGreaterEqual(summary["languages"], 10)

    def test_topic_availability_includes_published_counts(self):
        availability = topic_availability()
        data_structures = next(item for item in availability if item["topic"].name == "Data Structures")

        self.assertGreaterEqual(data_structures["published_count"], 1)
        self.assertIn("language_count", data_structures)

    def test_dashboard_stats_include_streak_best_and_breakdown(self):
        user = User(email="learner@example.com", password="hash", role="user")
        db.session.add(user)
        db.session.commit()
        attempt = create_attempt(user.id, [], "EASY", 1)
        answer = attempt.answers[0]
        correct = answer.question.correct_option

        submit_answer(attempt, answer.id, correct.id)

        stats = dashboard_stats(user.id)

        self.assertEqual(stats["best"], 100)
        self.assertEqual(stats["completed_this_week"], 1)
        self.assertGreaterEqual(stats["streak"], 1)
        self.assertTrue(stats["topic_breakdown"])


class AdminRouteAccessTest(DevBrainTestCase):
    def test_admin_rejects_anonymous_user(self):
        response = self.client.get("/admin")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_admin_link_renders_for_admin_only(self):
        admin = User(email="admin@example.com", username="Admin", password="hash", role="admin")
        learner = User(email="user@example.com", username="User", password="hash", role="user")
        db.session.add_all([admin, learner])
        db.session.commit()

        with self.client.session_transaction() as session:
            session["user_id"] = admin.id
            session["auth_marker"] = auth_marker(admin)
        admin_html = self.client.get("/dashboard").get_data(as_text=True)

        with self.client.session_transaction() as session:
            session["user_id"] = learner.id
            session["auth_marker"] = auth_marker(learner)
        learner_html = self.client.get("/dashboard").get_data(as_text=True)

        self.assertIn("Admin</a>", admin_html)
        self.assertNotIn("Admin</a>", learner_html)

    def test_admin_can_delete_empty_topic(self):
        admin = User(email="admin@example.com", username="Admin", password="hash", role="admin")
        topic = Topic(name="Temporary", slug="temporary", description="", is_active=True)
        db.session.add_all([admin, topic])
        db.session.commit()

        with self.client.session_transaction() as session:
            session["user_id"] = admin.id
            session["auth_marker"] = auth_marker(admin)
        response = self.client.post(
            "/admin/topics",
            data={"action": "delete", "topic_id": str(topic.id)},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(db.session.get(Topic, topic.id))

    def test_admin_can_delete_language_filter(self):
        admin = User(email="admin@example.com", username="Admin", password="hash", role="admin")
        language = Language(name="Elixir", slug="elixir", description="", is_active=True)
        db.session.add_all([admin, language])
        db.session.commit()

        with self.client.session_transaction() as session:
            session["user_id"] = admin.id
            session["auth_marker"] = auth_marker(admin)
        response = self.client.post(
            "/admin/languages",
            data={"action": "delete", "language_id": str(language.id)},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(db.session.get(Language, language.id))
