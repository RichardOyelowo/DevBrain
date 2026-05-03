from app.extensions import db
from app.learning import can_start_quiz, create_attempt, quiz_quota_status
from app.models import Language, Topic, User
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

    def test_free_user_cannot_start_after_five_attempts(self):
        user = User(email="learner@example.com", password="hash", role="user")
        db.session.add(user)
        db.session.commit()
        for _ in range(5):
            create_attempt(user.id, [], "EASY", 1)

        self.assertFalse(can_start_quiz(user.id))


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
        admin_html = self.client.get("/dashboard").get_data(as_text=True)

        with self.client.session_transaction() as session:
            session["user_id"] = learner.id
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
        response = self.client.post(
            "/admin/languages",
            data={"action": "delete", "language_id": str(language.id)},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(db.session.get(Language, language.id))
