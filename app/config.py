import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    API_KEY = os.environ.get("DEVBRAIN_API_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL")

    MAIL_SERVER = "smtp.mailgun.org"
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("EMAIL")
    MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
