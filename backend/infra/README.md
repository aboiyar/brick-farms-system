# Integration test helper

This folder contains scripts to start a local integration environment and run the test suite against it.

Prerequisites
- Docker & docker-compose installed
- Python virtualenv with project dependencies (or use Dockerized runners)

Run integration tests

```bash
# from repository root
chmod +x infra/scripts/integration_test.sh
infra/scripts/integration_test.sh
```

This will:
- Start Postgres (TimescaleDB image with PostGIS expected) and Redis
- Run alembic migrations (requires alembic in PATH)
- Seed simple activity and yields tables
- Run pytest

Notes
- The script uses local `alembic` binary; you may prefer to run alembic inside a Python container.
- Adjust database connection string in the script if your environment differs.
