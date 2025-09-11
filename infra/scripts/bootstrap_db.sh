#!/usr/bin/env bash
set -euo pipefail

DB=${DB_NAME:-brickfarm}
USER=${DB_USER:-brickfarm}
PASS=${DB_PASS:-brickfarm_pass}

sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
CREATE USER ${USER} WITH PASSWORD '${PASS}';
CREATE DATABASE ${DB} OWNER ${USER};
\c ${DB}
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
SQL
echo "Database bootstrap complete."
