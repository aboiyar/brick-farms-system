#!/usr/bin/env bash
set -euo pipefail

# Dev start script
# - Starts DB and Redis via docker-compose
# - Creates/activates a Python venv, installs requirements
# - Runs alembic migrations against the local docker Postgres
# - Starts the backend in reload mode (uvicorn)

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

echo "Starting Postgres and Redis containers..."
docker compose up -d db redis

POSTGRES_USER=${POSTGRES_USER:-brickfarm}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-brickfarm_pass}
POSTGRES_DB=${POSTGRES_DB:-brickfarm}
POSTGRES_PORT=${POSTGRES_PORT:-5433}

echo "Waiting for Postgres to be ready on host port ${POSTGRES_PORT}..."
until docker compose exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null 2>&1; do
  sleep 1
done

echo "Preparing Python virtualenv (.venv)..."
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

export DATABASE_URL="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@127.0.0.1:$POSTGRES_PORT/$POSTGRES_DB"

echo "Running alembic migrations..."
alembic -c alembic.ini upgrade head

echo "Starting backend (uvicorn) on http://0.0.0.0:8000"
# Run with reload for development. Use --host 0.0.0.0 so host can reach it from WSL/host.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
