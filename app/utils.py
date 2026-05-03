from .extensions import db
from .models import LegacyQuiz

def calculate_grade(score, total):
    percentage = (score / total) * 100

    if percentage < 40:
        return "Needs Improvement", percentage
    elif percentage < 60:
        return "Fair", percentage
    elif percentage < 75:
        return "Average", percentage
    elif percentage < 90:
        return "Competent", percentage
    else:
        return "Mastery", percentage


def save_quiz_result(user_id, topic, difficulty, limit, score, grade):
    if "&" in topic:
        topic = topic.replace("&", ", ")

    db.session.add(
        LegacyQuiz(
            user_id=user_id,
            topic=topic,
            difficulty=difficulty.upper(),
            question_count=limit,
            score=score,
            grade=grade,
        )
    )
    db.session.commit()
