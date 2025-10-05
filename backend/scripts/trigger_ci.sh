#!/usr/bin/env bash
set -euo pipefail

# trigger_ci.sh
# Usage: GITHUB_TOKEN=xxx ./scripts/trigger_ci.sh
# Triggers the repo-level integration workflow for the current branch (feat/reports-forecast-pdf)

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "Please set GITHUB_TOKEN env var with a PAT (scopes: repo, workflow)"
  exit 1
fi

OWNER=aboiyar
REPO=brick-farms-system
WORKFLOW_FILE=integration-backend.yml
REF=${1:-feat/reports-forecast-pdf}

curl -s -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_FILE/dispatches \
  -d "{\"ref\": \"$REF\"}" -w "\nHTTP: %{http_code}\n"
