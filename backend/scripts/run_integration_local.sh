#!/usr/bin/env bash
set -euo pipefail

# run_integration_local.sh
# Usage: ./scripts/run_integration_local.sh
# Brings up docker-compose (Postgres + Redis), creates venv, installs deps,
# runs alembic migrations, seeds DB, and runs pytest.

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

echo "Starting Docker services..."
docker compose up -d

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
pip install -e .

echo "Running alembic migrations"
export DATABASE_URL="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@127.0.0.1:$POSTGRES_PORT/$POSTGRES_DB"
alembic -c alembic.ini upgrade head

echo "Seeding DB (if seed file exists)"
if [ -f infra/scripts/seed_reports.sql ]; then
  psql "$DATABASE_URL" -f infra/scripts/seed_reports.sql || true
fi

echo "Running pytest (integration)"
PYTHONPATH=. pytest -q

echo "Integration run complete."
