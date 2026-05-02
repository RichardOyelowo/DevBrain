import os

port = os.getenv("PORT", "8000")
bind = os.getenv("GUNICORN_BIND", f"0.0.0.0:{port}")
workers = int(os.getenv("GUNICORN_WORKERS", 4))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 30))

accesslog = "-"
errorlog = "-"
