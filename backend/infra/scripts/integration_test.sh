#!/usr/bin/env bash
set -euo pipefail

# Starts docker-compose, waits for services, runs alembic migrations, seeds sample data, and runs pytest
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Waiting for Postgres to be ready..."
done
echo "Seeding sample data"

docker-compose up -d --build

# wait for db to be ready
echo "Waiting for Postgres to be ready..."
until docker exec $(docker ps -q -f ancestor=timescale/timescaledb) pg_isready -U brick >/dev/null 2>&1; do
  sleep 1
done

echo "Running alembic migrations inside a Python container"
# run alembic inside a python container that mounts this repository
docker run --rm -v "$ROOT_DIR":/app -w /app --network host python:3.11 bash -c "pip install --upgrade pip && pip install .[dev] || pip install . && alembic upgrade head"

echo "Seeding sample data inside a Python container"
docker run --rm -v "$ROOT_DIR":/app -w /app --network host python:3.11 bash -c "pip install --upgrade pip && pip install psycopg[binary] && psql \"postgresql://brick:brickpass@localhost:5432/brickfarm\" -f infra/scripts/seed_reports.sql"

echo "Running pytest on host (use venv or run inside container if preferred)"
pytest -q

# teardown
# docker-compose down
