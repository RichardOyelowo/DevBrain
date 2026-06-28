from collections import defaultdict, deque
from functools import wraps
from time import monotonic

from flask import current_app, request


_attempts = defaultdict(deque)


def clear_rate_limits():
    _attempts.clear()


def client_ip():
    if current_app.config.get("TRUST_PROXY_HEADERS"):
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "unknown"


def default_rate_keys(scope):
    email = (request.form.get("email") or "").strip().lower()
    remote_addr = client_ip()
    keys = [f"{scope}:ip:{remote_addr}"]
    if email:
        keys.append(f"{scope}:email:{email}")
    return keys


def rate_limit(scope):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if request.method != "POST":
                return view(*args, **kwargs)

            limit = current_app.config.get("AUTH_RATE_LIMIT", 5)
            window = current_app.config.get("AUTH_RATE_WINDOW_SECONDS", 900)
            now = monotonic()
            keys = default_rate_keys(scope)
            buckets = [_attempts[key] for key in keys]

            for bucket in buckets:
                while bucket and bucket[0] <= now - window:
                    bucket.popleft()

            if any(len(bucket) >= limit for bucket in buckets):
                return ("Too many attempts. Please wait and try again.", 429)

            for bucket in buckets:
                bucket.append(now)
            return view(*args, **kwargs)

        return wrapped

    return decorator
