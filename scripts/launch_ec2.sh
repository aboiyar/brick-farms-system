#!/usr/bin/env bash
set -euo pipefail

# launch_ec2.sh
# Single script to safely deploy BrickFarm backend + frontend on Ubuntu 24.04 (or run locally with --local).
# Usage:
#   ./scripts/launch_ec2.sh [--local] [--image-backend TAG] [--image-frontend TAG] [--no-seed]
# Examples:
#   # Run locally using docker compose (build images locally)
#   ./scripts/launch_ec2.sh --local
#
#   # Run on server (default): pull `latest` images from registry and deploy
#   ./scripts/launch_ec2.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.prod.yml"

BACKEND_IMG_TAG="ghcr.io/${GITHUB_OWNER:-brickservers}/brickfarm-backend:latest"
FRONTEND_IMG_TAG="ghcr.io/${GITHUB_OWNER:-brickservers}/brickfarm-frontend:latest"

LOCAL_MODE=false
DO_SEED=true

print_help(){
  sed -n '1,120p' "$0" | sed -n '1,40p'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local) LOCAL_MODE=true; shift ;;
    --image-backend) BACKEND_IMG_TAG="$2"; shift 2 ;;
    --image-frontend) FRONTEND_IMG_TAG="$2"; shift 2 ;;
    --no-seed) DO_SEED=false; shift ;;
    -h|--help) print_help; exit 0 ;;
    *) echo "Unknown arg: $1"; print_help; exit 2 ;;
  esac
done

echoinfo(){ echo "[INFO] $*"; }
echoerr(){ echo "[ERROR] $*" >&2; }

check_command(){
  if ! command -v "$1" >/dev/null 2>&1; then
    echoerr "Required command '$1' not found. Please install it and re-run."
    return 1
  fi
}

ensure_prereqs(){
  echoinfo "Checking prerequisites..."
  check_command docker || exit 1
  # prefer `docker compose`, fallback to `docker-compose`
  if command -v docker >/dev/null 2>&1; then
    if docker compose version >/dev/null 2>&1; then
      DOCKER_COMPOSE_CMD="docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
      DOCKER_COMPOSE_CMD="docker-compose"
    else
      echoerr "Neither 'docker compose' nor 'docker-compose' available. Install docker-compose or the Docker Compose plugin."
      exit 1
    fi
  fi

  # ensure docker daemon running
  if ! docker info >/dev/null 2>&1; then
    echoerr "Docker daemon doesn't seem to be running or you lack permissions. Ensure docker is running and you can run 'docker ps'."
    exit 1
  fi
}

wait_for_db(){
  local timeout=${1:-60}
  echoinfo "Waiting for Postgres to become ready (timeout=${timeout}s)..."
  local i=0
  while :; do
    if ${DOCKER_COMPOSE_CMD} -f "$COMPOSE_FILE" exec -T db pg_isready -U "${POSTGRES_USER:-postgres}" >/dev/null 2>&1; then
      echoinfo "Postgres is ready."
      return 0
    fi
    i=$((i+1))
    if [ $i -ge $timeout ]; then
      echoerr "Timed out waiting for Postgres to become ready"
      return 2
    fi
    sleep 1
  done
}

run_migrations(){
  echoinfo "Running Alembic migrations inside backend container..."
  # This will run alembic using the backend image/container environment
  ${DOCKER_COMPOSE_CMD} -f "$COMPOSE_FILE" run --rm backend python3 -m alembic upgrade head
}

run_seed(){
  if [ "$DO_SEED" = false ]; then
    echoinfo "Skipping seeding as requested."
    return 0
  fi
  if [ -x "$ROOT_DIR/demo_seed.sh" ]; then
    echoinfo "Running demo seeder on host (demo_seed.sh)..."
    (cd "$ROOT_DIR" && ./demo_seed.sh) || echoerr "demo_seed.sh returned non-zero (continue)"
  else
    echoinfo "Attempting to run seeder inside backend container (if available)..."
    ${DOCKER_COMPOSE_CMD} -f "$COMPOSE_FILE" run --rm backend bash -lc 'if [ -x ./demo_seed.sh ]; then ./demo_seed.sh; elif python3 -c "import app; print(\"ok\")" >/dev/null 2>&1; then echo "No demo_seed.sh found in image"; else echo "No seed available"; fi' || true
  fi
}

deploy_local(){
  echoinfo "Bringing up services locally (build and start)..."
  (cd "$ROOT_DIR" && ${DOCKER_COMPOSE_CMD} -f "$COMPOSE_FILE" up -d --build)
  wait_for_db 60
  run_migrations
  run_seed
  echoinfo "Local deployment complete."
}

deploy_server(){
  echoinfo "Server mode: pulling images and deploying from registry:"
  echoinfo "  backend -> $BACKEND_IMG_TAG"
  echoinfo "  frontend -> $FRONTEND_IMG_TAG"

  # set environment override for compose to use the images we want (optional)
  export BF_BACKEND_IMAGE="${BACKEND_IMG_TAG}"
  export BF_FRONTEND_IMAGE="${FRONTEND_IMG_TAG}"

  # Pull images first (faster on networks with cold cache)
  docker pull "$BACKEND_IMG_TAG" || echoinfo "Warning: could not pull backend image ($BACKEND_IMG_TAG)"
  docker pull "$FRONTEND_IMG_TAG" || echoinfo "Warning: could not pull frontend image ($FRONTEND_IMG_TAG)"

  echoinfo "Starting DB container..."
  (cd "$ROOT_DIR" && ${DOCKER_COMPOSE_CMD} -f "$COMPOSE_FILE" up -d db)
  wait_for_db 120

  # Run migrations using the backend image/container
  run_migrations

  echoinfo "Bringing all services up..."
  (cd "$ROOT_DIR" && ${DOCKER_COMPOSE_CMD} -f "$COMPOSE_FILE" up -d --remove-orphans)

  run_seed

  echoinfo "Server deployment complete."
}

main(){
  ensure_prereqs

  if [ "$LOCAL_MODE" = true ]; then
    deploy_local
  else
    deploy_server
  fi
}

main
