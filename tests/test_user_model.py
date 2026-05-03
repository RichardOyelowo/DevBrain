from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User
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
    def test_first_registered_user_becomes_admin(self):
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
