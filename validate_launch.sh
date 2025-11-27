#!/usr/bin/env bash
###############################################################################
# BRICKFARM LAUNCH VALIDATION CHECKLIST
#
# This script performs pre-launch checks to ensure everything is ready.
# Run this 30 minutes before the 7AM stakeholder demo.
#
# Usage: ./validate_launch.sh
###############################################################################

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0

log_pass() { 
  echo -e "${GREEN}✓${NC} $*"
  ((PASSED++))
}

log_fail() { 
  echo -e "${RED}✗${NC} $*"
  ((FAILED++))
}

log_warn() { 
  echo -e "${YELLOW}⚠${NC} $*"
}

log_section() { 
  echo ""
  echo -e "${BLUE}=== $* ===${NC}"
}

###############################################################################
# CHECKS
###############################################################################

log_section "SYSTEM REQUIREMENTS"

# Check Docker
if command -v docker &> /dev/null; then
  DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+')
  log_pass "Docker installed: version $DOCKER_VERSION"
else
  log_fail "Docker not installed"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
  log_pass "Docker Compose installed"
else
  log_fail "Docker Compose not installed"
fi

# Check Python
if command -v python3 &> /dev/null; then
  PY_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
  if (( $(echo "$PY_VERSION >= 3.11" | bc -l) )); then
    log_pass "Python $PY_VERSION installed (>= 3.11 required)"
  else
    log_fail "Python $PY_VERSION found but 3.11+ required"
  fi
else
  log_fail "Python3 not installed"
fi

# Check Node.js
if command -v node &> /dev/null; then
  NODE_VERSION=$(node --version | grep -oP '\d+\.\d+')
  log_pass "Node.js $NODE_VERSION installed"
else
  log_fail "Node.js not installed"
fi

# Check Yarn/NPM
if command -v yarn &> /dev/null; then
  log_pass "Yarn installed"
elif command -v npm &> /dev/null; then
  log_pass "NPM installed"
else
  log_fail "Neither Yarn nor NPM installed"
fi

log_section "CONFIGURATION FILES"

# Check .env
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
  if grep -q "DB_PORT=5433" "$PROJECT_ROOT/backend/.env"; then
    log_pass "backend/.env exists with correct DB_PORT=5433"
  else
    log_fail "backend/.env has wrong DB_PORT (should be 5433)"
  fi
  
  if grep -q "JWT_SECRET=" "$PROJECT_ROOT/backend/.env"; then
    log_pass "backend/.env has JWT_SECRET configured"
  else
    log_fail "backend/.env missing JWT_SECRET"
  fi
else
  log_fail "backend/.env file not found"
fi

# Check frontend .env.local
if [ -f "$PROJECT_ROOT/frontend-web/.env.local" ]; then
  if grep -q "VITE_API_URL=" "$PROJECT_ROOT/frontend-web/.env.local"; then
    log_pass "frontend-web/.env.local has VITE_API_URL configured"
  else
    log_fail "frontend-web/.env.local missing VITE_API_URL"
  fi
else
  log_fail "frontend-web/.env.local file not found"
fi

log_section "PROJECT FILES"

# Check key files exist
FILES=(
  "backend/pyproject.toml"
  "backend/requirements.txt"
  "backend/alembic.ini"
  "backend/docker-compose.yml"
  "backend/app/main.py"
  "backend/app/config.py"
  "backend/app/db/session.py"
  "backend/app/db/base.py"
  "frontend-web/package.json"
  "frontend-web/vite.config.ts"
  "frontend-web/src/main.tsx"
  "launch.sh"
  "demo_seed.sh"
  "LAUNCH_GUIDE.md"
  "LAUNCH_REPORT.md"
)

for file in "${FILES[@]}"; do
  if [ -f "$PROJECT_ROOT/$file" ]; then
    log_pass "$file exists"
  else
    log_fail "$file missing"
  fi
done

log_section "MIGRATIONS"

# Check migrations exist
if [ -f "$PROJECT_ROOT/backend/app/db/migrations/versions/0001_init_core.py" ]; then
  log_pass "Migration 0001_init_core.py exists"
else
  log_fail "Critical migration 0001_init_core.py missing"
fi

MIGRATION_COUNT=$(ls "$PROJECT_ROOT/backend/app/db/migrations/versions/"/*.py 2>/dev/null | wc -l)
if [ "$MIGRATION_COUNT" -ge 5 ]; then
  log_pass "$MIGRATION_COUNT migration files found"
else
  log_warn "Only $MIGRATION_COUNT migrations found (expected ~5)"
fi

log_section "PORT AVAILABILITY"

# Check if ports are available
for port in 5173 8000 5433 6380; do
  if ! lsof -i :$port &> /dev/null; then
    log_pass "Port $port available"
  else
    log_warn "Port $port is in use (will try to restart services)"
  fi
done

log_section "VIRTUAL ENVIRONMENT"

# Check if venv exists
if [ -d "$PROJECT_ROOT/backend/.venv" ]; then
  log_pass "Python venv already exists (backend/.venv)"
  if [ -f "$PROJECT_ROOT/backend/.venv/bin/activate" ]; then
    log_pass "Venv activation script found"
  else
    log_fail "Venv appears corrupted"
  fi
else
  log_warn "Venv not created yet (will be created by launch.sh)"
fi

log_section "NODE MODULES"

# Check if dependencies installed
if [ -d "$PROJECT_ROOT/frontend-web/node_modules" ]; then
  log_pass "Frontend dependencies installed (node_modules exists)"
else
  log_warn "Frontend dependencies not installed (will be installed by launch.sh)"
fi

log_section "SCRIPTS"

# Check if launch scripts are executable
for script in launch.sh demo_seed.sh; do
  if [ -x "$PROJECT_ROOT/$script" ]; then
    log_pass "$script is executable"
  else
    log_warn "$script not executable (fixing...)"
    chmod +x "$PROJECT_ROOT/$script"
    log_pass "$script made executable"
  fi
done

log_section "DOCKER SERVICES STATUS"

# Check if Docker services can be started
if docker-compose -f "$PROJECT_ROOT/backend/docker-compose.yml" config > /dev/null 2>&1; then
  log_pass "docker-compose.yml is valid"
else
  log_fail "docker-compose.yml has syntax errors"
fi

# Try to get Docker images status
if docker-compose -f "$PROJECT_ROOT/backend/docker-compose.yml" images 2>/dev/null | grep -q postgis; then
  log_pass "PostGIS Docker image is available"
else
  log_warn "PostGIS Docker image not pulled yet (will pull on first run)"
fi

if docker-compose -f "$PROJECT_ROOT/backend/docker-compose.yml" images 2>/dev/null | grep -q redis; then
  log_pass "Redis Docker image is available"
else
  log_warn "Redis Docker image not pulled yet (will pull on first run)"
fi

log_section "SUMMARY"

echo ""
echo "Checks passed: ${GREEN}$PASSED${NC}"
echo "Checks failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✓ ALL CHECKS PASSED - READY TO LAUNCH!${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Run: ./launch.sh"
  echo "  2. Wait for services to start (30 seconds)"
  echo "  3. Run: ./demo_seed.sh"
  echo "  4. Open: http://localhost:5173"
  echo ""
  exit 0
else
  echo -e "${YELLOW}⚠ SOME CHECKS FAILED - PLEASE REVIEW ABOVE${NC}"
  echo ""
  echo "Failed checks:"
  grep "^✗" <(echo "$(exec 2>&1)") || true
  echo ""
  exit 1
fi
