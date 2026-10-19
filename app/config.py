import os
from datetime import timedelta


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    ENVIRONMENT = os.environ.get("FLASK_ENV", "development")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if ENVIRONMENT == "production" and not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is required in production.")
    SECRET_KEY = SECRET_KEY or "devbrain-local-secret"
    ADMIN_BOOTSTRAP_ENABLED = _env_bool("ADMIN_BOOTSTRAP_ENABLED", False)
    AUTH_RATE_LIMIT = int(os.environ.get("AUTH_RATE_LIMIT", 5))
    AUTH_RATE_WINDOW_SECONDS = int(os.environ.get("AUTH_RATE_WINDOW_SECONDS", 900))
    TRUST_PROXY_HEADERS = _env_bool("TRUST_PROXY_HEADERS", False)
    WTF_CSRF_SSL_STRICT = _env_bool("WTF_CSRF_SSL_STRICT", ENVIRONMENT == "production")

    raw_database_url = os.environ.get("DATABASE_URL", "sqlite:///instance/devbrain.db")
    if raw_database_url.startswith("postgres://"):
        raw_database_url = raw_database_url.replace("postgres://", "postgresql://", 1)
    elif "://" not in raw_database_url:
        raw_database_url = f"sqlite:///{raw_database_url}"

    DATABASE_URL = raw_database_url
    SQLALCHEMY_DATABASE_URI = raw_database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }
    
    MAIL_USE_TLS = _env_bool("MAIL_USE_TLS", True)
    MAIL_USE_SSL = _env_bool("MAIL_USE_SSL", False)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or os.environ.get("EMAIL", "")
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or os.environ.get("EMAIL_PASSWORD", "")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_TIMEOUT = int(os.environ.get("MAIL_TIMEOUT", 8))
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") or MAIL_USERNAME or "noreply@devbrain.online"

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", ENVIRONMENT == "production")
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    PREFERRED_URL_SCHEME = "https"
