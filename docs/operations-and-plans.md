# Plans And Production Operations

This guide describes the plan limits and the startup path in this repository.

## Plans

`app/learning.py` checks the plan saved on each user:

- Free: 5 quiz starts in a rolling 7-day window
- Pro: 50 quiz starts in a rolling 7-day window
- Unlimited: no weekly cap
- Admin: no weekly cap

An attempt uses a slot when it starts, including an unfinished attempt. The slot becomes available after seven days.

The pricing page lists Pro at $4.99 per month and Unlimited at $9.99 per month as planned prices. Checkout is not connected. No payment provider changes `users.plan`; access must be set through trusted application or database operations.

## Required settings

Set a unique `SECRET_KEY` in production. The app refuses to start in production without one. Session cookies use `Secure` by default in production, and strict CSRF referrer checks are enabled by default there.

`TRUST_PROXY_HEADERS` defaults to false. Enable it only when the app is behind a trusted proxy that sets forwarded client IP headers.

The auth limiter defaults to 5 POST attempts per IP and email in 900 seconds. It stores counters in each Gunicorn worker's memory. Counters are not shared between workers or app instances.

For the full environment variable list, see the Configuration section in [the README](../readme.md).

## Admin bootstrap

The first registered account is a regular user by default. On a new, empty database only, set `ADMIN_BOOTSTRAP_ENABLED=true` before the intended admin registers. Turn it off as soon as the account is created.

The setting does not promote an account on a database that already has users. Do not leave it enabled while registration is open.

## Database startup

`start.sh` runs `flask db upgrade` and `flask ensure-catalog` before Gunicorn starts. The catalog command adds starter rows only when core catalog data is missing.

For an existing production database, take a database backup before applying migrations. Do not run `flask init-db` as a deployment step.

Migration `20260628_0008_unique_lower_user_email.py` normalizes existing email values and adds a case-insensitive unique index. It stops if two rows would share the same lowercased, trimmed address. Resolve duplicates before retrying the migration. Downgrading removes the index but does not restore earlier casing or whitespace.

## Local checks

Run the repository test suite with:

```bash
python -m unittest discover -s tests -v
```

The current tests use in-memory SQLite. Production uses PostgreSQL.
