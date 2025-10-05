Local development — backend

Prereqs:
- Docker / docker-compose (or Podman with docker-compose compat)
- Python 3.11/3.12 and venv

Quick start:

```bash
# start DB + Redis (from project root)
cd backend
docker compose up -d

# create a venv and install deps (example)
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# run alembic migrations
alembic upgrade head

# seed test data (optional)
psql "postgresql://brickfarm:brickfarm_pass@localhost:5432/brickfarm" -f infra/scripts/seed_reports.sql

# run the app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Notes:
- The docker-compose Postgres service uses user `brickfarm` and password `brickfarm_pass` to match `backend/.env.example`.
- CI runs an integration job that starts the same services, runs alembic, seeds the DB and executes pytest.

Helper scripts:

From the `backend/` directory:

- Run local integration (requires Docker):
	./scripts/run_integration_local.sh

- Trigger CI workflow (requires GITHUB_TOKEN env var):
	GITHUB_TOKEN=xxx ./scripts/trigger_ci.sh

- Create PR from branch (requires GITHUB_TOKEN env var and `jq`):
	GITHUB_TOKEN=xxx ./scripts/create_pr.sh

