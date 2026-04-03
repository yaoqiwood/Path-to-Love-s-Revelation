#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

APP_ENV="${APP_ENV:-development}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8011}"
WORKERS="${WORKERS:-1}"
RELOAD="${RELOAD:-}"

if [[ -z "$RELOAD" ]]; then
  if [[ "$APP_ENV" == "development" ]]; then
    RELOAD="1"
  else
    RELOAD="0"
  fi
fi

cmd=("$SCRIPT_DIR/.venv/bin/python" -m uvicorn main:app --host "$HOST" --port "$PORT")

if [[ "$RELOAD" == "1" || "$RELOAD" == "true" || "$RELOAD" == "True" ]]; then
  cmd+=(--reload)
else
  cmd+=(--workers "$WORKERS")
fi

exec "${cmd[@]}"
