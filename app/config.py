import os
from datetime import timedelta

class Config:
    # Required environment variables
    SECRET_KEY = os.environ.get("SECRET_KEY")
    API_KEY = os.environ.get("DEVBRAIN_API_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    MAIL_USERNAME = os.environ.get("EMAIL")
    MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))  # Optional default

    # Check all required env vars
    required_vars = {
        "SECRET_KEY": SECRET_KEY,
        "API_KEY": API_KEY,
        "DATABASE_URL": DATABASE_URL,
        "MAIL_USERNAME": MAIL_USERNAME,
        "MAIL_PASSWORD": MAIL_PASSWORD,
        "MAIL_SERVER": MAIL_SERVER
    }

    missing_vars = [name for name, val in required_vars.items() if not val]
    if missing_vars:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Mail config
    MAIL_USE_TLS = True

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    PREFERRED_URL_SCHEME = "https"
