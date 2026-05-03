from app.learning import create_attempt, get_next_pending_answer, submit_answer
from app.models import LegacyQuiz, QuizAttempt, Topic
from tests.base import DevBrainTestCase


class QuizAttemptModelTest(DevBrainTestCase):
    def test_percentage_returns_zero_when_no_questions_exist(self):
        attempt = QuizAttempt(topic_label="Empty", difficulty="EASY", question_count=0, score=0)

        self.assertEqual(attempt.percentage, 0)

    def test_create_attempt_creates_pending_answers(self):
        attempt = create_attempt(None, [], "EASY", 3)

        self.assertEqual(attempt.status, "in_progress")
        self.assertEqual(attempt.question_count, 3)
        self.assertEqual(len(attempt.answers), 3)

    def test_answered_count_tracks_submitted_answers(self):
        attempt = create_attempt(None, [], "EASY", 2)
        pending = get_next_pending_answer(attempt)

        submit_answer(attempt, pending.id, pending.question.correct_option.id)

        self.assertEqual(attempt.answered_count, 1)

    def test_attempt_grades_when_final_answer_is_submitted(self):
        attempt = create_attempt(None, [], "EASY", 1)
        pending = get_next_pending_answer(attempt)

        submit_answer(attempt, pending.id, pending.question.correct_option.id)

        self.assertEqual(attempt.status, "completed")
        self.assertEqual(attempt.score, 1)
        self.assertEqual(attempt.grade, "Mastery")

    def test_attempt_fills_requested_count_from_broader_pool(self):
        topic = Topic.query.filter_by(name="Data Structures").first()

        attempt = create_attempt(None, [topic.id], "EASY", 5)

        self.assertEqual(attempt.question_count, 5)

    def test_language_filter_prioritizes_matching_code_questions(self):
        topic = Topic.query.filter_by(name="Data Structures").first()
        target = next(question for question in topic.questions if question.language == "python")
        target.language = "Python"
        from app.extensions import db
        db.session.commit()

        attempt = create_attempt(None, [topic.id], "EASY", 1, "python")

        self.assertEqual(attempt.question_count, 1)
        self.assertEqual(attempt.answers[0].question.topic.name, "Data Structures")
        self.assertEqual(attempt.answers[0].question.language.lower(), "python")

    def test_language_filter_falls_back_to_topic_questions(self):
        topic = Topic.query.filter_by(name="Data Structures").first()

        attempt = create_attempt(None, [topic.id], "EASY", 2, "python")

        self.assertEqual(attempt.question_count, 2)
        self.assertTrue(all(answer.question.topic.name == "Data Structures" for answer in attempt.answers))


class LegacyQuizModelTest(DevBrainTestCase):
    def test_legacy_summary_is_written_for_logged_in_completed_attempt(self):
        from app.extensions import db
        from app.models import User

        user = User(email="learner@example.com", password="hash", role="user")
        db.session.add(user)
        db.session.commit()
        attempt = create_attempt(user.id, [], "EASY", 1)
        pending = get_next_pending_answer(attempt)

        submit_answer(attempt, pending.id, pending.question.correct_option.id)

        summary = LegacyQuiz.query.filter_by(user_id=user.id).first()
        self.assertIsNotNone(summary)
        self.assertEqual(summary.score, 1)
