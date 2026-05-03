import json

from app.extensions import db
from app.learning import import_questions_from_payload
from app.models import AnswerOption, Question, QuestionImportBatch, Topic, User
from tests.base import DevBrainTestCase


class QuestionImportModelTest(DevBrainTestCase):
    def test_import_questions_records_import_batch(self):
        user = User(email="admin@example.com", password="hash", role="admin")
        db.session.add(user)
        db.session.commit()

        batch = import_questions_from_payload(user.id, [_question_payload()])

        self.assertEqual(batch.status, "completed")
        self.assertEqual(batch.count, 1)
        self.assertEqual(QuestionImportBatch.query.count(), 1)

    def test_import_questions_saves_unpublished_questions(self):
        user = User(email="admin@example.com", password="hash", role="admin")
        db.session.add(user)
        db.session.commit()

        import_questions_from_payload(user.id, {"questions": [_question_payload(topic="Static Typing")]})
        drafts = Question.query.filter_by(source="import", status="draft").all()

        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0].topic.name, "Static Typing")
        self.assertEqual(drafts[0].language, "python")
        self.assertEqual(drafts[0].correct_option.text, "It narrows the possible type.")

    def test_import_questions_accepts_correct_option_index(self):
        user = User(email="admin@example.com", password="hash", role="admin")
        db.session.add(user)
        db.session.commit()
        payload = _question_payload()
        payload["options"] = ["One", "Two", "Three", "Four"]
        payload["correct_option"] = "2"

        import_questions_from_payload(user.id, [payload])
        question = Question.query.filter_by(source="import").one()
        options = AnswerOption.query.filter_by(question_id=question.id).order_by(AnswerOption.position).all()

        self.assertEqual(options[2].text, "Three")
        self.assertTrue(options[2].is_correct)

    def test_import_questions_rejects_missing_correct_option(self):
        user = User(email="admin@example.com", password="hash", role="admin")
        db.session.add(user)
        db.session.commit()
        payload = _question_payload()
        payload["options"] = [
            {"text": "A", "is_correct": False},
            {"text": "B", "is_correct": False},
        ]

        with self.assertRaises(ValueError):
            import_questions_from_payload(user.id, [payload])

    def test_admin_import_route_saves_drafts(self):
        user = User(email="admin@example.com", password="hash", role="admin")
        db.session.add(user)
        db.session.commit()
        with self.client.session_transaction() as client_session:
            client_session["user_id"] = user.id

        response = self.client.post(
            "/admin/import",
            data={"payload": json.dumps([_question_payload(topic="HTTP")])},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Question.query.filter_by(source="import", status="draft").count(), 1)


def _question_payload(topic="Type Systems"):
    return {
        "topic": topic,
        "difficulty": "MEDIUM",
        "prompt": "What does type narrowing do?",
        "description": "Choose the best answer.",
        "explanation": "Type narrowing reduces possible types after a check.",
        "language": "python",
        "code_snippet": "if value is not None:\n    print(value)",
        "options": [
            {"text": "It narrows the possible type.", "is_correct": True},
            {"text": "It deletes a variable.", "is_correct": False},
            {"text": "It disables validation.", "is_correct": False},
            {"text": "It encrypts a value.", "is_correct": False},
        ],
    }
