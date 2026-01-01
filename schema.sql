CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    topic TEXT,
    difficulty TEXT CHECK(difficulty IN ('EASY', 'MEDIUM', 'HARD')),
    question_count INTEGER NOT NULL DEFAULT 0,
    score INTEGER NOT NULL,
    grade TEXT NOT NULL CHECK (
        grade IN ('Needs Improvement', 'Fair', 'Average', 'Competent', 'Mastery')
    ),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_quizzes_user_id
ON quizzes(user_id);
