<div align=center>

# <img src="images/full_logo.svg" alt="DevBrain Logo" style="vertical-align: middle;"> 

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

DevBrain is a production-ready web quiz application for developers who want to actually test their programming knowledge. Built with Flask, Redis, and SQLite, featuring multi-worker support and real-time feedback.

---
</div>

![Demo](images/image.webp)

## Description

DevBrain is a quiz app I built because I got tired of passively consuming programming tutorials without really knowing if anything stuck. Most learning platforms focus on watching and reading—there's no real way to test yourself beyond toy exercises that don't reflect actual knowledge gaps.

So I made something different: a straightforward quiz platform with instant feedback, optional account tracking, and the ability to actually see your progress over time. You can jump in without registering, or create an account if you want to track your performance across multiple sessions.

The big architectural shift from the original version: **Redis-backed state management and multi-worker support**. Questions are cached in Redis so they're only fetched once, and sessions are stored in Redis instead of the filesystem, making the whole thing actually scalable. You can now run this with multiple Gunicorn workers without quiz state getting messed up.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Tech Stack & Architecture](#tech-stack--architecture)
  - [Why This Stack?](#why-this-stack)
  - [Architecture Overview](#architecture-overview)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Grade Scale](#grade-scale)
- [Project Structure](#project-structure)
- [Key Routes](#key-routes)
- [Database](#database)
  - [Schema](#database-schema)
  - [WAL Mode for Concurrency](#wal-mode-for-concurrency)
- [Redis Architecture](#redis-architecture)
  - [Quiz Question Cache](#1-quiz-question-cache)
  - [Session Storage](#2-session-storage)
- [Security Features](#security-features)
- [Production Deployment](#production-deployment)
  - [Gunicorn Configuration](#gunicorn-configuration)
  - [Reverse Proxy Setup](#reverse-proxy-setup-nginx-example)
- [Architecture Decisions](#architecture-decisions)
- [Known Limitations](#known-limitations)
- [Future Improvements](#future-improvements)
- [What I Learned](#what-i-learned)
- [Troubleshooting](#troubleshooting)
- [Author](#author)
- [License](#license)

---

## Quick Start
```bash
# Clone and setup
git clone <repository-url>
cd project
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Setup environment variables (create .env file)
cat > .env << EOF
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DEVBRAIN_API_KEY=your-api-key-here
DATABASE_URL=instance/devbrain.db
REDIS_URL=redis://localhost:6379/0
EMAIL=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
FLASK_ENV=development
EOF

# Start Redis (must be running)
redis-server  # or brew services start redis on macOS

# Initialize database and run
python run.py

# For production with multiple workers
gunicorn run:app

# You might need to explicitly call the config file on your end
gunicorn --config gunicorn.conf.py run:app
```

Visit `http://localhost:5000` (dev) or `http://localhost:8000` (production)

---

## Features

- ✅ **Multi-topic quizzes** – Mix and match topics, choose difficulty levels  
- ✅ **Instant feedback** – Know immediately if you're right or wrong  
- ✅ **Anonymous or registered** – Try quizzes without an account, or register to save history  
- ✅ **Performance tracking** – See all past attempts, scores, and grades over time  
- ✅ **Password reset via email** – Secure token-based password recovery  
- ✅ **Production-ready** – Multi-worker support with Gunicorn + Redis  
- ✅ **Concurrent database access** – SQLite in WAL mode handles multiple workers  
- ✅ **Special character support** – Fixed HTML entity issues for quotes/apostrophes in answers  

---

## Tech Stack & Architecture

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Python, Flask | Web framework |
| **Frontend** | HTML, Jinja2, Bootstrap | Templates and styling |
| **Database** | SQLite (WAL mode) | User accounts and quiz history |
| **Cache/Sessions** | Redis | Quiz cache + session store |
| **Server** | Gunicorn | Production WSGI server (multi-worker) |
| **Forms** | Flask-WTF, WTForms | Form handling and CSRF protection |
| **Security** | Werkzeug, itsdangerous | Password hashing, secure tokens |
| **Email** | Flask-Mail | Password reset emails |

### Why This Stack?

**Flask** – Lightweight, doesn't force opinions, perfect for this scope  
**SQLite + WAL** – Zero configuration, WAL mode enables concurrent access  
**Redis** – Solves multi-worker state synchronization elegantly  
**Gunicorn** – Battle-tested production server with worker process management  

The combination of Redis for ephemeral state and SQLite for persistent data is perfect for this use case. Redis keeps quiz questions cached and sessions synchronized across workers, while SQLite handles user accounts and quiz history with zero configuration overhead.

### Architecture Overview
```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│         nginx (reverse proxy)    │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│      Gunicorn (4 workers)        │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐│
│  │ W1  │ │ W2  │ │ W3  │ │ W4  ││
│  └─────┘ └─────┘ └─────┘ └─────┘│
└────┬──────────────┬──────────────┘
     │              │
     │              │
┌────▼─────┐   ┌───▼──────────┐
│  Redis   │   │ SQLite (WAL) │
│          │   │              │
│ Sessions │   │ Users        │
│ Quiz     │   │ Quiz History │
│ Cache    │   │              │
└──────────┘   └──────────────┘
```

**Key Design Points:**
- **Stateless workers:** All state lives in Redis or SQLite, not in worker memory
- **Shared quiz cache:** Questions fetched once, used by all workers (1-hour TTL)
- **WAL mode:** SQLite allows concurrent reads/writes across workers
- **Redis sessions:** Sessions work correctly regardless of which worker handles the request

---

## Installation & Setup

### Prerequisites

- Python 3.7+
- Redis server
- Git

### Step 1: Clone and Setup Virtual Environment
```bash
git clone <repository-url>
cd project

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup Redis

**Option A: Local Redis**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Windows
# Download from https://github.com/microsoftarchive/redis/releases
```

**Option B: Redis Cloud (recommended for production)**
- Sign up at [redislabs.com](https://redislabs.com) or use your cloud provider's Redis service
- Get your Redis connection URL (format: `redis://user:password@host:port`)

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:
```bash
SECRET_KEY=your-secret-key-here  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
DEVBRAIN_API_KEY=your-quiz-api-key-from-quizapi.io
DATABASE_URL=instance/devbrain.db
REDIS_URL=redis://localhost:6379/0  # or your Redis Cloud URL
EMAIL=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
FLASK_ENV=development  # or production
```

**Getting a Gmail App Password:**
1. Enable 2FA on your Google account
2. Go to Google Account → Security → 2-Step Verification → App passwords
3. Generate a new app password for "Mail"
4. Use that password (not your regular Gmail password)

### Step 5: Initialize Database
```bash
python run.py
```

This automatically creates the database file and tables if they don't exist.

### Step 6: Run the Application

**Development mode (single worker):**
```bash
python run.py
# Visit http://localhost:5000
```

**Production mode (multi-worker with Gunicorn):**
```bash
gunicorn --config gunicorn.conf.py run:app
# Visit http://localhost:8000
```

---

## Configuration

All configuration lives in `app/config.py` and pulls from environment variables.

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session encryption key | `abc123...` (64 chars) |
| `DEVBRAIN_API_KEY` | API key from quizapi.io | Get from [quizapi.io](https://quizapi.io) |
| `DATABASE_URL` | Path to SQLite database | `instance/devbrain.db` |
| `EMAIL` | Email address for sending password resets | `yourapp@gmail.com` |
| `EMAIL_PASSWORD` | App-specific password for email | Gmail app password |
| `MAIL_SERVER` | SMTP server address | `smtp.gmail.com` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `MAIL_PORT` | `587` | SMTP port |
| `FLASK_ENV` | `production` | Set to `development` to auto-load `.env` |

The config class validates all required variables on startup and raises a clear error if anything's missing:
```python
missing_vars = [name for name, val in required_vars.items() if not val]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")
```

---

## Usage

### Taking a Quiz

1. Visit the homepage at `http://localhost:5000` or `http://localhost:8000`
2. Click **"Start Quiz"**
3. Select one or more topics from the list
4. Choose difficulty: Easy, Medium, or Hard
5. Set number of questions (1-50)
6. Click **"Start Quiz"**
7. Answer each question and get instant feedback
8. See your final score, percentage, and grade

### Creating an Account (Optional)

1. Click **"Register"** in the navigation
2. Enter your email, username, and password
3. Confirm your password
4. Click **"Register"**
5. You'll be automatically logged in and redirected to the quiz page

**Why register?**
- All completed quizzes are saved to your history
- Track your performance over time
- See which topics you're strongest/weakest in
- View detailed statistics per quiz attempt

### Viewing Quiz History

1. Log in to your account
2. Click **"History"** in the navigation
3. See all past quiz attempts with:
   - Date and time
   - Topic(s) covered
   - Difficulty level
   - Number of questions
   - Score and percentage
   - Grade received

### Password Reset

1. Click **"Forgot Password?"** on the login page
2. Enter your email address
3. Check your email for a reset link (valid for 1 hour)
4. Click the link and enter your new password
5. You'll be redirected to login with your new password

### Grade Scale

| Grade | Percentage | Meaning |
|-------|-----------|---------|
| **Mastery** | 90-100% | Excellent understanding |
| **Competent** | 75-89% | Strong grasp of the material |
| **Average** | 60-74% | Decent understanding, room for improvement |
| **Fair** | 40-59% | Basic knowledge, needs more practice |
| **Needs Improvement** | 0-39% | Significant gaps, review recommended |

---

## Project Structure
```
project/
│
├── app/                        # Main application package
│   ├── __init__.py            # Application factory (create_app)
│   ├── routes.py              # Main routes (quiz, history, about)
│   ├── auth.py                # Authentication routes (login, register, password reset)
│   ├── question.py            # Questions class for API interaction
│   ├── config.py              # Configuration from environment variables
│   ├── db.py                  # Database connection and initialization
│   ├── extensions.py          # Flask extensions (mail, CSRF, Redis)
│   ├── forms.py               # WTForms for login/register/password reset
│   ├── utils.py               # Helper functions (grading, saving results)
│   ├── schema.sql             # Database schema (users, quizzes tables)
│   │
│   ├── templates/             # Jinja2 HTML templates
│   │   ├── base.html         # Base template with navbar
│   │   ├── index.html        # Homepage
│   │   ├── quiz.html         # Quiz interface
│   │   ├── results.html      # Quiz results page
│   │   ├── history.html      # Quiz history (logged-in users)
│   │   ├── login.html        # Login form
│   │   ├── register.html     # Registration form
│   │   ├── forgot_password.html  # Password reset (multiple states)
│   │   ├── reset_email.html  # Password reset email template (HTML)
│   │   ├── reset_email.txt   # Password reset email template (plain text)
│   │   └── about.html        # About page
│   │
│   └── static/               # CSS, JavaScript, images
│       ├── css/
│       │   └── styles.css   # Main stylesheet
│       └── js/
│           └── quiz.js      # Quiz interaction logic
│
├── instance/                 # Instance-specific files (created at runtime)
│   └── devbrain.db          # SQLite database (auto-generated)
│
├── venv/                    # Virtual environment (gitignored)
│
├── run.py                   # Application entry point
├── gunicorn.conf.py         # Gunicorn configuration for production
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (gitignored)
├── readme.md               # This file
└── images/                 # Screenshots and assets
    ├── full_logo.png
    └── screenshot.png
```

---

## Key Routes

### Public Routes (no login required)

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/` | Homepage |
| `GET` | `/about` | About page |
| `GET` | `/quiz` | Quiz topic selection page |
| `POST` | `/quiz` | Start quiz or submit answer |
| `GET` | `/login` | Login page |
| `POST` | `/login` | Process login form |
| `GET` | `/register` | Registration page |
| `POST` | `/register` | Process registration form |
| `GET` | `/forgot_password` | Password reset request page |
| `POST` | `/forgot_password` | Send password reset email |
| `GET` | `/reset_password/<token>` | Password reset form |
| `POST` | `/reset_password/<token>` | Update password |

### Protected Routes (login required)

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/history` | View quiz history |
| `GET` | `/logout` | Clear session and log out |

---

## Database

The app uses **SQLite with WAL (Write-Ahead Logging) mode** for concurrent access. The database file is automatically created on first run using the schema in `app/schema.sql`.

### Database Initialization

In `run.py`:
```python
from app import create_app
from app.db import create_db

app = create_app()

with app.app_context():
    create_db()  # Creates database if it doesn't exist
```

### WAL Mode for Concurrency

Every database connection enables WAL mode:
```python
g.db.execute("PRAGMA journal_mode=WAL;")
```

**Why WAL mode?**
- Allows multiple workers to read simultaneously
- Writers don't block readers
- Atomic commits prevent corruption
- Critical for Gunicorn multi-worker deployments

### Database Schema

**users table:**
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT,
    password TEXT NOT NULL  -- Hashed with Werkzeug
);
```

**quizzes table:**
```sql
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    topic TEXT,  -- Comma-separated if multiple topics
    difficulty TEXT CHECK(difficulty IN ('EASY', 'MEDIUM', 'HARD')),
    question_count INTEGER NOT NULL DEFAULT 0,
    score INTEGER NOT NULL,
    grade TEXT NOT NULL CHECK (
        grade IN ('Needs Improvement', 'Fair', 'Average', 'Competent', 'Mastery')
    ),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_quizzes_user_id ON quizzes(user_id);
```

---

## Redis Architecture

Redis handles two critical pieces of state in a multi-worker environment:

### 1. Quiz Question Cache

When a user starts a quiz, questions are fetched from the external API once and stored in Redis with a 1-hour TTL:
```python
# In app/routes.py
quiz_cache.setex(f"quiz:{session_key}", 3600, json.dumps(questions))
```

**Benefits:**
- Questions fetched only once, regardless of number of workers
- Prevents API rate limiting
- Improves response time (no repeated API calls)
- Consistent quiz experience (same questions throughout the session)

**Key format:** `quiz:{session_key}`  
**TTL:** 3600 seconds (1 hour)  
**Data:** JSON-serialized list of question objects

### 2. Session Storage

Flask-Session is configured to use Redis instead of filesystem:
```python
# In app/__init__.py
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis_client
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)
```

**Why Redis sessions?**
- **Multi-worker compatibility:** Any worker can read any session
- **No filesystem locks:** Eliminates race conditions
- **Automatic expiration:** Sessions auto-expire based on config
- **Scalability:** Easy to add more workers without session issues

**Without Redis sessions:**
- Worker A creates session file
- Worker B can't read Worker A's session file
- User loses quiz progress randomly
- Shopping cart analogy: imagine your cart disappearing when the load balancer routes you to a different server

---

## Security Features

- ✅ **Password hashing** – Werkzeug's `generate_password_hash` with salt
- ✅ **CSRF protection** – Flask-WTF on all authenticated routes
- ✅ **Secure password reset** – Time-limited tokens (1 hour) using `itsdangerous`
- ✅ **HTTPOnly cookies** – Session cookies not accessible via JavaScript
- ✅ **SameSite cookies** – Set to `Lax` to prevent CSRF attacks
- ✅ **Secure flag in production** – Cookies only sent over HTTPS
- ✅ **Redis session encryption** – Sessions signed with `SECRET_KEY`
- ✅ **Email obfuscation** – Password reset always shows "email sent" (prevents user enumeration)
- ✅ **SQL injection protection** – All queries use parameterized statements
- ✅ **XSS protection** – Jinja2 auto-escapes all variables by default
- ✅ **No secrets in code** – All sensitive config in environment variables

---

## Production Deployment

### Gunicorn Configuration

The included `gunicorn.conf.py` has production-ready defaults:
```python
workers = 4  # Adjust based on CPU cores (recommended: 2-4 × num_cores)
bind = "0.0.0.0:8000"
worker_class = "sync"
timeout = 30
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
```

**Starting with Gunicorn:**
```bash
gunicorn --config gunicorn.conf.py run:app
```

### Environment Variables for Production

Set these in your production environment (not in `.env` file):
```bash
export FLASK_ENV=production
export SECRET_KEY="generate-a-new-secure-key"
export SESSION_COOKIE_SECURE=True
export REDIS_URL="redis://your-production-redis:6379/0"
export DATABASE_URL="/var/www/devbrain/instance/devbrain.db"
export DEVBRAIN_API_KEY="your-api-key"
export EMAIL="noreply@yourdomain.com"
export EMAIL_PASSWORD="your-production-smtp-password"
export MAIL_SERVER="smtp.your-email-provider.com"
```

**Security checklist:**
- [ ] Generate a new `SECRET_KEY` (don't reuse dev key)
- [ ] Set `SESSION_COOKIE_SECURE=True` (requires HTTPS)
- [ ] Use a production Redis instance (not localhost)
- [ ] Ensure database file is writable by Gunicorn user
- [ ] Configure firewall to only allow nginx → Gunicorn traffic

### Reverse Proxy Setup (nginx example)
```nginx
upstream devbrain {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;  # Force HTTPS
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://devbrain;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /static {
        alias /var/www/devbrain/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Get SSL certificate (Let's Encrypt):**
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Architecture Decisions

This section explains why certain technical choices were made.

### Application Factory Pattern

The app uses Flask's application factory pattern (`create_app()` in `__init__.py`):
```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    mail.init_app(app)
    csrf.init_app(app)
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    if REDIS_URL:
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = redis_client
        Session(app)
    
    return app
```

**Benefits:**
- Configuration can be injected at runtime
- Multiple app instances can be created for testing
- Extensions are initialized in the correct order
- Follows Flask best practices

### Why Redis for Both Sessions and Cache?

Initially I tried filesystem sessions (Flask-Session's default), but it caused weird issues with multiple Gunicorn workers. Sessions would disappear between requests because worker A couldn't read worker B's session files.

Redis solves this elegantly:
- **Sessions:** Shared across all workers, no state sync issues
- **Quiz cache:** Questions fetched once, used by all workers
- **Single dependency:** One Redis instance handles both use cases

The alternative would've been memcached for caching + database for sessions, but Redis is simpler and works out of the box for both.

### SQLite with WAL Mode

Using SQLite in production is controversial, but WAL mode makes it viable:

**Advantages:**
- Zero configuration (no connection strings, users, permissions)
- File-based (easy backups, easy to move)
- Surprisingly fast for <100 concurrent users
- Built into Python (no extra dependencies)

**How WAL mode helps:**
- Concurrent reads don't block each other
- Writes don't block reads
- Atomic commits prevent corruption

**When to migrate to Postgres:**
- 100+ concurrent users
- Geographic distribution (multiple data centers)
- Complex queries that need advanced indexes
- Need for replication/high availability

For a side project or small team, SQLite + WAL is honestly perfect.

### The Special Characters Bug Fix

This was painful to debug. Original code used `|tojson` on button attributes:
```html
<button data-answer="{{ answer|tojson }}">
```

**Problems this caused:**
1. `|tojson` adds literal quote characters: `"Use 'chmod'"` instead of `Use 'chmod'`
2. Special characters get HTML-encoded: `'` becomes `&#39;`

**Result:**
- `data-answer` attribute: Browser auto-decodes to `Use 'chmod'`
- Correct answer from Jinja: `Use &#39;chmod&#39;`
- JavaScript comparison fails even though they're logically identical

**The fix (three-part):**
1. Use `|e` instead of `|tojson` (escapes without adding quotes)
2. Decode HTML entities in JavaScript:
```javascript
function decodeHTML(html) {
    const txt = document.createElement('textarea');
    txt.innerHTML = html;
    return txt.value;
}
```
3. Use `html.unescape()` on form submissions in Python

Now answers with special characters work correctly everywhere.

### CSRF Protection Strategy

CSRF is enabled globally but `/quiz` route is exempted:
```python
@main.route("/quiz", methods=["GET", "POST"])
@csrf.exempt
def quiz():
```

**Why?**
- Quiz needs to work for anonymous users
- Anonymous users don't have sessions yet
- Enforcing CSRF tokens would break the initial quiz submission

Once you're logged in, CSRF protection applies to `/history` and `/logout`.

### The Single-Template Password Reset

`forgot_password.html` handles four states using a `form_type` parameter:
1. **"forgot"** – Initial email input
2. **"sent_or_notfound"** – Confirmation (always shown)
3. **"reset"** – Password reset form
4. **"success"** – Password updated confirmation

This saves creating four separate templates for what's essentially the same page. The routes are separate (`/forgot_password` and `/reset_password/<token>`), but they render the same template with different parameters.

---

## Known Limitations

- ⚠️ **Email only works with Gmail by default** – Other SMTP providers need config changes
- ⚠️ **Depends on external API** – If quizapi.io is down, the app doesn't work
- ⚠️ **No admin panel** – Can't add/edit questions through the UI
- ⚠️ **SQLite not suitable for huge scale** – WAL mode helps, but 1000+ concurrent users need Postgres
- ⚠️ **No question explanations displayed** – API provides them, but UI doesn't show them yet

---

## Future Improvements

- [ ] Display question explanations after answers
- [ ] Add custom quiz creation (user-generated questions)
- [ ] Optional leaderboard system
- [ ] Support multiple quiz APIs (not just quizapi.io)
- [ ] Better mobile styling (current design is functional but not optimized)
- [ ] Export quiz history as CSV or PDF
- [ ] "Practice weak topics" feature (auto-generate quizzes from worst categories)
- [ ] Real-time multiplayer quiz rooms (would require WebSockets)
- [ ] Dark mode toggle
- [ ] Quiz sharing (share specific quiz configurations with others)

---

## What I Learned

### The Multi-Worker Realization

The original version worked fine in development (single process), but completely broke in production with `gunicorn -w 4`:
- Quiz questions fetched 4 times (once per worker)
- Sessions randomly disappeared (worker A couldn't read worker B's files)
- Race conditions in SQLite (before WAL mode)

Adding Redis solved all of these. Good lesson: **what works in dev doesn't always work in prod.**

### The HTML Entity Nightmare

Debugging why `Use 'chmod'` wasn't matching took way too long. The issue was subtle—both looked correct in HTML source, but one had `&#39;` in JavaScript.

Required understanding:
1. How Jinja filters work (`|tojson` vs `|e` vs `|safe`)
2. How browsers decode HTML attributes automatically
3. How to decode HTML entities in JavaScript
4. When to use `html.unescape()` in Python

Now I always test with special characters during development.

### SQLite Can Be Production-Ready

I was skeptical, but WAL mode changed my mind. For apps with <100 concurrent users (most side projects):
- Zero configuration
- File-based (easy backups)
- Surprisingly fast
- Built into Python

The key is enabling WAL mode and using `check_same_thread=False`.

### Session Management Is Nuanced

Initially I tried signed cookies (size limits with full quiz questions), then filesystem sessions (multi-worker issues), then Redis (perfect).

Trade-offs matter. **There's no one-size-fits-all solution.**

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'app'"
**Problem:** Running Python from wrong directory  
**Solution:** Make sure you're in the project root (where `run.py` is)
```bash
cd /path/to/project
python run.py
```

### "RuntimeError: Missing required environment variables"
**Problem:** Environment variables not set  
**Solution:** Check your `.env` file has all required vars:
```bash
# Required:
SECRET_KEY=...
DEVBRAIN_API_KEY=...
DATABASE_URL=...
EMAIL=...
EMAIL_PASSWORD=...
MAIL_SERVER=...
```

### "Connection refused" when connecting to Redis
**Problem:** Redis not running or wrong URL  
**Solution:**
```bash
# Check if Redis is running
redis-cli ping  # Should return PONG

# Start Redis if not running
redis-server  # or brew services start redis
```

### Quiz questions not appearing
**Problem:** API key invalid or rate limited  
**Solution:**
```bash
# Test API directly
curl "https://quizapi.io/api/v1/questions?apiKey=YOUR_KEY&limit=1"

# If rate limited, wait a few minutes
# If invalid key, get a new one from quizapi.io
```

### Sessions not persisting
**Problem:** Redis not accessible or misconfigured  
**Solution:**
1. Verify Redis is running: `redis-cli ping`
2. Check `REDIS_URL` environment variable
3. Test connection:
```python
import redis
r = redis.Redis.from_url('redis://localhost:6379/0', decode_responses=True)
r.ping()  # Should return True
```

### "Database is locked" errors
**Problem:** WAL mode not enabled or using network filesystem  
**Solution:**
1. Check `db.py` enables WAL: `g.db.execute("PRAGMA journal_mode=WAL;")`
2. Verify database is on local filesystem (not NFS/network mount)
3. Check file permissions (database file must be writable)

### Workers crashing or timing out
**Problem:** Incorrect Gunicorn configuration  
**Solution:**
```python
# In gunicorn.conf.py
workers = 4  # Too many workers can cause issues
timeout = 30  # Increase if API calls are slow
worker_class = "sync"  # Don't use async workers with SQLite
```

---

## Author

Built by Richard as an evolution of my CS50 Final Project.

The original version was a single-file Flask app perfect for learning, but not production-ready. This version demonstrates:
- Application factory pattern
- Multi-worker architecture
- Redis integration
- Production deployment best practices
- Proper separation of concerns

If you have questions, find bugs, or want to contribute, feel free to open an issue or reach out.

---

## License

MIT License – use it, modify it, break it, deploy it, whatever.