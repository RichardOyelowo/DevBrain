from collections import defaultdict, deque
from functools import wraps
from time import monotonic

from flask import current_app, request


_attempts = defaultdict(deque)


def clear_rate_limits():
    _attempts.clear()


def default_rate_key(scope):
    email = (request.form.get("email") or "").strip().lower()
    remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    return f"{scope}:{remote_addr}:{email}"


def rate_limit(scope):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if request.method != "POST":
                return view(*args, **kwargs)

            limit = current_app.config.get("AUTH_RATE_LIMIT", 5)
            window = current_app.config.get("AUTH_RATE_WINDOW_SECONDS", 900)
            now = monotonic()
            key = default_rate_key(scope)
            bucket = _attempts[key]

            while bucket and bucket[0] <= now - window:
                bucket.popleft()

            if len(bucket) >= limit:
                return ("Too many attempts. Please wait and try again.", 429)

            bucket.append(now)
            return view(*args, **kwargs)

        return wrapped

    return decorator
