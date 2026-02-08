import os

SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")
EMAIL = os.environ.get("EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
DEVBRAIN_API_KEY = os.environ.get("API_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")
