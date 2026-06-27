from unittest.mock import patch

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app.auth import create_reset_token, send_reset_email
from app.extensions import db
from app.models import User
from app.rate_limit import clear_rate_limits
from tests.base import DevBrainTestCase


class UserModelTest(DevBrainTestCase):
    def test_is_admin_returns_true_for_admin_role(self):
        user = User(email="admin@example.com", password="hash", role="admin")

        self.assertTrue(user.is_admin)

    def test_is_admin_returns_false_for_normal_user(self):
        user = User(email="user@example.com", password="hash", role="user")

        self.assertFalse(user.is_admin)

    def test_user_persists_with_default_role(self):
        user = User(
            email="new@example.com",
            username="NewUser",
            password=generate_password_hash("Pass123!"),
        )
        db.session.add(user)
        db.session.commit()

        saved = User.query.filter_by(email="new@example.com").first()

        self.assertIsNotNone(saved)
        self.assertEqual(saved.role, "user")
        self.assertEqual(saved.username, "NewUser")


class UserAuthRouteTest(DevBrainTestCase):
    def tearDown(self):
        clear_rate_limits()
        super().tearDown()

    def test_first_registered_user_is_normal_user_by_default(self):
        response = self.client.post(
            "/register",
            data={
                "email": "first@example.com",
                "username": "First",
                "password": "Pass123!",
                "confirmation": "Pass123!",
            },
            follow_redirects=False,
        )
        user = User.query.filter_by(email="first@example.com").first()

        self.assertEqual(response.status_code, 302)
        self.assertFalse(user.is_admin)

    def test_first_registered_user_can_be_bootstrap_admin(self):
        self.app.config["ADMIN_BOOTSTRAP_ENABLED"] = True

        response = self.client.post(
            "/register",
            data={
                "email": "first@example.com",
                "username": "First",
                "password": "Pass123!",
                "confirmation": "Pass123!",
            },
            follow_redirects=False,
        )
        user = User.query.filter_by(email="first@example.com").first()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(user.is_admin)

    def test_second_registered_user_is_normal_user(self):
        db.session.add(User(email="first@example.com", password="hash", role="admin"))
        db.session.commit()

        self.client.post(
            "/register",
            data={
                "email": "second@example.com",
                "username": "Second",
                "password": "Pass123!",
                "confirmation": "Pass123!",
            },
        )
        user = User.query.filter_by(email="second@example.com").first()

        self.assertIsNotNone(user)
        self.assertEqual(user.role, "user")

    def test_login_rate_limit_returns_429(self):
        clear_rate_limits()
        self.app.config["AUTH_RATE_LIMIT"] = 1
        self.app.config["AUTH_RATE_WINDOW_SECONDS"] = 60

        first = self.client.post("/login", data={"email": "learner@example.com", "password": "bad"})
        second = self.client.post("/login", data={"email": "learner@example.com", "password": "bad"})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)


class PasswordResetRouteTest(DevBrainTestCase):
    def tearDown(self):
        clear_rate_limits()
        super().tearDown()

    def test_reset_email_uses_configured_socket_timeout(self):
        self.app.config["MAIL_TIMEOUT"] = 3

        with self.app.test_request_context(), patch("app.auth.mail.send") as mail_send, patch("app.auth.socket.setdefaulttimeout") as set_timeout:
            send_reset_email("learner@example.com", "https://example.com/reset")

        mail_send.assert_called_once()
        set_timeout.assert_any_call(3)
        set_timeout.assert_any_call(None)

    def test_forgot_password_sends_reset_email_for_existing_user(self):
        user = User(email="learner@example.com", password=generate_password_hash("Old123!"))
        db.session.add(user)
        db.session.commit()

        with patch("app.auth.queue_reset_email") as queue_reset_email:
            response = self.client.post(
                "/forgot_password",
                data={"email": "learner@example.com"},
                follow_redirects=False,
            )

        self.assertEqual(response.status_code, 200)
        queue_reset_email.assert_called_once()
        self.assertEqual(queue_reset_email.call_args.kwargs["to_email"], "learner@example.com")
        self.assertIn("/reset_password/", queue_reset_email.call_args.kwargs["reset_link"])

    def test_forgot_password_is_neutral_for_unknown_email(self):
        with patch("app.auth.queue_reset_email") as queue_reset_email:
            response = self.client.post(
                "/forgot_password",
                data={"email": "missing@example.com"},
                follow_redirects=False,
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"If an account exists", response.data)
        queue_reset_email.assert_not_called()

    def test_invalid_reset_token_renders_recovery_form(self):
        response = self.client.get("/reset_password/not-a-real-token")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The reset link is invalid or expired.", response.data)
        self.assertIn(b"Reset Your Password", response.data)

    def test_reset_password_updates_user_password(self):
        user = User(email="learner@example.com", password=generate_password_hash("Old123!"))
        db.session.add(user)
        db.session.commit()
        token = create_reset_token(user)

        response = self.client.post(
            f"/reset_password/{token}",
            data={"password": "New123!", "confirmation": "New123!"},
            follow_redirects=False,
        )
        saved = db.session.get(User, user.id)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(check_password_hash(saved.password, "New123!"))

    def test_reset_token_cannot_be_reused_after_password_change(self):
        user = User(email="learner@example.com", password=generate_password_hash("Old123!"))
        db.session.add(user)
        db.session.commit()
        token = create_reset_token(user)

        self.client.post(
            f"/reset_password/{token}",
            data={"password": "New123!", "confirmation": "New123!"},
        )
        response = self.client.post(
            f"/reset_password/{token}",
            data={"password": "Again123!", "confirmation": "Again123!"},
        )
        saved = db.session.get(User, user.id)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The reset link is invalid or expired.", response.data)
        self.assertFalse(check_password_hash(saved.password, "Again123!"))
