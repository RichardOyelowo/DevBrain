import hashlib


def auth_marker(user):
    changed_at = user.password_changed_at or user.created_at
    changed_at_marker = int(changed_at.timestamp()) if changed_at else 0
    password_marker = hashlib.sha256(user.password.encode("utf-8")).hexdigest()
    return f"{changed_at_marker}:{password_marker}"
