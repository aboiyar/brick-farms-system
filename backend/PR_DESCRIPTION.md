PR: feat/reports-forecast-pdf -> main

Summary

This PR adds reports forecasting (Holt–Winters), PDF export support, user preferences (API + migration), and tile caching helpers. It also updates CI and dependencies to ensure integration tests run cleanly.

Key changes
- API: `app/api/v1/reports.py` — forecasting endpoints, CSV/PDF export
- API: `app/api/v1/preferences.py` — preferences endpoints
- DB: migration `0005_create_user_preferences.py` (creates `user_preferences` table)
- DB: fixed migration order (`0004` down_revision updated to `0003`) to ensure linear Alembic history
- CI: `backend/.github/workflows/integration.yml` — updated to use backend/requirements.txt, correct DB credentials, run migrations and seed before tests
- Dependencies: `backend/requirements.txt` updated (bumped reportlab to 4.4.4 to be compatible with current Python)
- Logging: `app/logging.py` added `exception_logger` helper for structured errors

Testing
- Unit tests pass locally in an isolated venv: `PYTHONPATH=backend backend/.venv_test/bin/pytest -q` (9 passed)
- Integration: CI workflow will start a TimescaleDB + Redis service, run migrations, seed, and execute pytest.

Notes for reviewers
- Confirm Alembic migrations and order before merging. Running `alembic heads` and `alembic current` in CI should show expected state.
- No secrets were added; `.gitignore` prevents environment artifacts from being committed.

Suggested gh CLI to open PR (run locally):

```
# from repo root
git checkout feat/reports-forecast-pdf
git push origin feat/reports-forecast-pdf
gh pr create --base main --head feat/reports-forecast-pdf --title "Reports: forecast + PDF, Preferences, CI" --body-file backend/PR_DESCRIPTION.md
```
