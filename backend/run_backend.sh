#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

APP_ENV="${APP_ENV:-development}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8011}"
WORKERS="${WORKERS:-1}"

exec "$SCRIPT_DIR/.venv/bin/python" -m uvicorn main:app --host "$HOST" --port "$PORT" --workers "$WORKERS"
