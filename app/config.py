import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "devbrain-local-secret")

    raw_database_url = os.environ.get("DATABASE_URL", "sqlite:///instance/devbrain.db")
    if raw_database_url.startswith("postgres://"):
        raw_database_url = raw_database_url.replace("postgres://", "postgresql://", 1)
    elif "://" not in raw_database_url:
        raw_database_url = f"sqlite:///{raw_database_url}"

    DATABASE_URL = raw_database_url
    SQLALCHEMY_DATABASE_URI = raw_database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get("EMAIL", "")
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_DEFAULT_SENDER = ("DevBrain Support", MAIL_USERNAME)

    MAIL_USE_TLS = True

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    PREFERRED_URL_SCHEME = "https"
