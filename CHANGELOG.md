# Changelog

This file records the notable changes in each existing release and the work prepared for the next release. Existing tag names and dates are kept as they appear in Git. The tags are not in semantic version order: `v0.1-public` was created after `v1.0.1`.

## v2.0.0 - 2026-10-18

Prepared for the next major release. This section is not tagged or released yet.

### Added

- New responsive design system and shared page components for marketing, account, quiz, review, history, profile, and admin pages.
- Free, Pro, and Unlimited plan quotas. Pro allows 50 quizzes per week. Unlimited has no quiz limit.
- Authentication rate limits, CSRF checks on protected admin actions, POST-only logout, stronger session validation, and password reset invalidation after password changes.
- User plan storage and migrations, including checks for normalized duplicate email addresses in legacy data.
- Setup, deployment, plans, and product guides updated to match the current application.
- `psycopg[binary]` for PostgreSQL URLs using psycopg 3.

### Changed

- Reworked marketing and application pages to use the shared design system and navigation.
- Updated page typography tokens to improve readability across the site.
- Avoided loading dashboard catalog counts when the dashboard does not use them.
- Added SQLAlchemy connection health and recycle settings.

### Fixed

- Tightened quiz and admin route permissions and authentication edge cases.
- Hardened plan migrations and email normalization checks.
- Corrected frontend regression expectations and PostgreSQL driver setup.

## v0.1-public - 2026-05-25

### Added

- Queued password reset emails and a full project README with database tables and initial data guidance.
- Row-level security support for Supabase PostgreSQL.

### Changed

- Added and updated runtime dependencies and Railway startup configuration.
- Set a timeout for password reset email requests and reorganized backend imports.
- Ignored local question packs.

### Fixed

- Corrected the password reset flow and a Flask form placeholder mismatch.

## v1.0.1 - 2026-05-02

### Added

- PostgreSQL-backed application setup, SQLAlchemy models, and starter data.
- User account and authentication routes, quiz handling, question management, and admin routes.
- User dashboard metrics, profile page, quiz review, and administration pages for managing questions.
- Initial automated test suite and CI workflow.

### Changed

- Replaced the initial SQLite application storage with PostgreSQL.
- Added the first full application templates, static assets, theme images, and Gunicorn configuration.
- Added the initial deployment setup and license.

## v0.0.1 - 2026-03-27

### Added

- Initial public application release with user registration, login, quiz sessions, scoring, and answer history.
- Question API integration, Redis-backed sessions, application layouts, and deployment setup.

### Changed

- Established the first Flask application structure and core quiz flow.
