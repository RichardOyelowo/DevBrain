from config import DATABASE_URL
from app import current_app


# database
DATABASE_PATH = DATABASE_URL

def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    if not os.path.exists(DATABASE_PATH):
        with sqlite3.connect(DATABASE_PATH) as conn:
            with open("schema.sql", "r") as f:
                conn.executescript(f.read())
                

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

