#!/usr/bin/env bash
set -euo pipefail

# create_pr.sh
# Usage: GITHUB_TOKEN=xxx ./scripts/create_pr.sh
# Creates a PR from the current branch to main with the PR description in backend/PR_DESCRIPTION.md

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "Please set GITHUB_TOKEN env var with a PAT"
  exit 1
fi

OWNER=aboiyar
REPO=brick-farms-system
BRANCH=${1:-feat/reports-forecast-pdf}
BASE=${2:-main}
TITLE="Reports: forecast + PDF, Preferences, CI"
BODY_FILE="backend/PR_DESCRIPTION.md"

BODY=$(jq -Rs . < "$BODY_FILE")

curl -s -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{\"title\": \"$TITLE\", \"head\": \"$BRANCH\", \"base\": \"$BASE\", \"body\": $BODY}" -w "\nHTTP: %{http_code}\n"
