#!/usr/bin/env bash
set -euo pipefail

# start_dev_local.sh
# Bring up DB and Redis via docker-compose (uses postgis image), prepare venv,
# run alembic migrations (skipping TimescaleDB if desired), and start the
# backend in dev mode with uvicorn --reload.

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

echo "Starting Docker services (db + redis)..."
docker compose up -d db redis

POSTGRES_USER=${POSTGRES_USER:-brickfarm}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-brickfarm_pass}
POSTGRES_DB=${POSTGRES_DB:-brickfarm}
POSTGRES_PORT=${POSTGRES_PORT:-5433}

echo "Waiting for Postgres to be ready..."
until docker compose exec -T db pg_isready -U "$POSTGRES_USER" >/dev/null 2>&1; do
  sleep 1
done

echo "Preparing Python venv..."
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# If your local DB image does not include TimescaleDB set SKIP_TIMESCALE=1 to
# avoid migration errors related to missing timescaledb.control.
export SKIP_TIMESCALE=${SKIP_TIMESCALE:-1}

export DATABASE_URL="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@127.0.0.1:$POSTGRES_PORT/$POSTGRES_DB"

echo "Running alembic migrations (SKIP_TIMESCALE=$SKIP_TIMESCALE)"
alembic -c alembic.ini upgrade head

echo "Starting backend (uvicorn) in reload mode..."
# Use host 0.0.0.0 so the frontend in WSL or host can reach it
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
