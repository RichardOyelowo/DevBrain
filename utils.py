
def calculate_grade(score, total):
    """Calculate grade based on percentage score"""
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
    """Save quiz results to database for logged-in users"""
    conn = get_db()
    cur = conn.cursor()
    
    #for multiple topics combined
    if "&" in topic:
        topic = topic.replace("&", ", ")

    cur.execute("INSERT INTO quizzes (user_id, topic, difficulty, question_count, score, grade) VALUES (?, ?, ?, ?, ?, ?)", 
        (user_id, topic, difficulty.upper(), limit, score, grade))
    conn.commit()
    conn.close()


def clear_quiz_session():
    session.pop("questions", None)
    session.pop("quiz_index", None)
    session.pop("quiz_score", None)
    session.pop("quiz_data", None)
