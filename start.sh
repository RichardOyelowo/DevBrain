#!/usr/bin/env bash
set -euo pipefail

export FLASK_APP="${FLASK_APP:-run.py}"

flask --app "$FLASK_APP" db upgrade
flask --app "$FLASK_APP" ensure-catalog

if [[ "${RUN_SEED_ON_START:-0}" == "1" ]]; then
    flask --app "$FLASK_APP" init-db
fi

exec gunicorn --config gunicorn.conf.py run:app
