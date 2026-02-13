import os

SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")
MAIL_SERVER="smtp.mailgun.org"
MAIL_USERNAME = os.environ.get("EMAIL")
MAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
API_KEY = os.environ.get("DEVBRAIN_API_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")
