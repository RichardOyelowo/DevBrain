# Plans and production setup

DevBrain saves a plan on each user account. `app/learning.py` enforces the quiz limits. Free allows 5 quiz starts in a rolling 7-day window. Pro allows 50. Unlimited has no weekly cap. Admin accounts also have no cap.

The limit counts quiz attempts when they start. An unfinished attempt uses a slot until it leaves the 7-day window. Attempts and reviews stay in account history.

## Billing status

The plans page lists Pro and Unlimited as planned. Checkout is not connected, so users cannot buy a plan in the app. The `plan` field changes quota behavior, but no payment flow updates it.

## Admin account setup

New accounts get the `user` role by default. To bootstrap an admin on an empty database, set `ADMIN_BOOTSTRAP_ENABLED=true` before the intended first account registers. Turn it off as soon as that account exists. Do not leave it enabled while public registration is open. The first account is selected by registration order.

Existing user roles are not changed by this setting. If the database already has accounts, the setting does not promote a new account.

## Production settings

Set `SECRET_KEY` in production. The app refuses to start without it. Session cookies use `Secure` by default in production. Keep `WTF_CSRF_SSL_STRICT` enabled when serving HTTPS.

Auth routes allow 5 POST attempts per 15 minutes for each client IP and email. The limiter keeps its counters in the Gunicorn worker process. `gunicorn.conf.py` starts one worker by default. If the worker count changes, each worker has a separate counter.

`TRUST_PROXY_HEADERS` is off by default. Turn it on only when the app receives traffic through a trusted proxy that sets `X-Forwarded-For`.

## Database upgrade

`start.sh` runs `flask db upgrade` before starting Gunicorn. The email migration normalizes existing addresses and adds a case-insensitive unique index. It stops if two rows would have the same lowercased, trimmed email. Resolve those accounts before retrying the migration. Downgrading removes the index but does not restore the old email casing or whitespace.

For an existing production database, back it up before applying migrations. Do not run `flask init-db` as a deployment step. That command creates the starter question bank when needed.
