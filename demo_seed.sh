#!/usr/bin/env bash
###############################################################################
# BRICKFARM DEMO SEED SCRIPT
#
# This script populates the database with demo data for stakeholder presentation.
# It will create:
#   - A tenant: "BrickServers Demo Farm"
#   - A user: demo@brickfarm.ng
#   - A farm: "Gboko Demonstration Farm"
#   - A field plot: "Maize Field A" with geolocation
#   - A crop: "Maize"
#   - A sensor device: "Soil Moisture Sensor #1"
#   - 10 sample sensor readings
#
# Usage: ./demo_seed.sh [http://localhost:8000]
###############################################################################

set -euo pipefail

API_BASE="${1:-http://localhost:8000/api/v1}"
DEMO_PASS="Demo123!"
DEMO_EMAIL="demo@brickfarm.ng"
DEMO_TENANT="BrickServers Demo Farm"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $*"; }

# Helper function to make API calls
api_call() {
  local method=$1
  local endpoint=$2
  local data=$3
  local token=$4
  
  local headers="-H 'Content-Type: application/json'"
  if [ -n "$token" ]; then
    headers="$headers -H 'Authorization: Bearer $token'"
  fi
  
  local cmd="curl -s -X $method $API_BASE$endpoint $headers"
  if [ -n "$data" ]; then
    cmd="$cmd -d '$data'"
  fi
  
  eval "$cmd"
}

# Test API connectivity
log_step "Testing API connectivity..."
if ! curl -s "$API_BASE/../.." >/dev/null 2>&1; then
  log_error "Cannot reach API at $API_BASE"
  log_error "Ensure backend is running: ./launch.sh"
  exit 1
fi
log_info "✓ API is reachable"

# Step 1: Signup (create new tenant)
log_step "Creating demo tenant and user..."
SIGNUP_RESPONSE=$(api_call POST "/auth/signup" '{
  "tenant_name": "'$DEMO_TENANT'",
  "email": "'$DEMO_EMAIL'",
  "password": "'$DEMO_PASS'"
}')

TOKEN=$(echo "$SIGNUP_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
  log_warn "Signup failed or user already exists. Attempting login..."
  
  LOGIN_RESPONSE=$(api_call POST "/auth/token" '{
    "email": "'$DEMO_EMAIL'",
    "password": "'$DEMO_PASS'"
  }')
  
  TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
  if [ -z "$TOKEN" ]; then
    log_error "Failed to signup or login"
    log_error "Response: $LOGIN_RESPONSE"
    exit 1
  fi
  log_warn "Using existing user"
else
  log_info "✓ Tenant created: $DEMO_TENANT"
  log_info "✓ User created: $DEMO_EMAIL"
fi

echo "Token: ${TOKEN:0:20}..."

# Step 2: Create a farm
log_step "Creating demo farm..."
FARM_RESPONSE=$(api_call POST "/farms/" '{
  "name": "Gboko Demonstration Farm",
  "country": "NG",
  "state": "Benue",
  "lga": "Gboko"
}' "$TOKEN")

FARM_ID=$(echo "$FARM_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -z "$FARM_ID" ]; then
  log_error "Failed to create farm"
  log_error "Response: $FARM_RESPONSE"
  exit 1
fi
log_info "✓ Farm created: $FARM_ID"

# Step 3: Create a field plot with geolocation
log_step "Creating demo field plot with geolocation..."
FIELD_RESPONSE=$(api_call POST "/fields/" '{
  "farm_id": "'$FARM_ID'",
  "name": "Maize Field A",
  "geom_geojson": {
    "type": "Polygon",
    "coordinates": [
      [
        [8.200, 7.700],
        [8.210, 7.700],
        [8.210, 7.710],
        [8.200, 7.710],
        [8.200, 7.700]
      ]
    ]
  }
}' "$TOKEN")

PLOT_ID=$(echo "$FIELD_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
AREA_HA=$(echo "$FIELD_RESPONSE" | grep -o '"area_ha":[0-9.]*' | cut -d':' -f2)
if [ -z "$PLOT_ID" ]; then
  log_error "Failed to create field plot"
  log_error "Response: $FIELD_RESPONSE"
  exit 1
fi
log_info "✓ Field plot created: $PLOT_ID"
log_info "  Area: $AREA_HA hectares"

# Step 4: Create a crop
log_step "Creating demo crop..."
CROP_RESPONSE=$(api_call POST "/crops/" '{
  "category": "crop",
  "common_name": "Maize (Corn)",
  "scientific_name": "Zea mays",
  "descriptors": {
    "days_to_maturity": {"required": true, "unit": "days", "value": 90},
    "planting_depth": {"required": true, "unit": "cm", "value": 5}
  }
}' "$TOKEN")

CROP_ID=$(echo "$CROP_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -z "$CROP_ID" ]; then
  log_error "Failed to create crop"
  log_error "Response: $CROP_RESPONSE"
  exit 1
fi
log_info "✓ Crop created: $CROP_ID (Maize)"

# Step 5: Create a sensor device
log_step "Creating demo sensor device..."
DEVICE_RESPONSE=$(api_call POST "/sensors/devices" '{
  "farm_id": "'$FARM_ID'",
  "plot_id": "'$PLOT_ID'",
  "name": "Soil Moisture Sensor #1",
  "protocol": "http",
  "api_key": "demo_sensor_key_12345"
}' "$TOKEN")

DEVICE_ID=$(echo "$DEVICE_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -z "$DEVICE_ID" ]; then
  log_error "Failed to create sensor device"
  log_error "Response: $DEVICE_RESPONSE"
  exit 1
fi
log_info "✓ Sensor device created: $DEVICE_ID"

# Step 6: Ingest sample sensor readings
log_step "Ingesting sample sensor readings..."
TIMESTAMPS=(
  "2025-11-27T08:00:00Z"
  "2025-11-27T09:00:00Z"
  "2025-11-27T10:00:00Z"
  "2025-11-27T11:00:00Z"
  "2025-11-27T12:00:00Z"
  "2025-11-27T13:00:00Z"
  "2025-11-27T14:00:00Z"
  "2025-11-27T15:00:00Z"
  "2025-11-27T16:00:00Z"
  "2025-11-27T17:00:00Z"
)

READINGS=(18.5 19.2 20.1 21.3 22.5 23.1 21.8 20.4 19.7 19.0)

for i in "${!TIMESTAMPS[@]}"; do
  INGEST_RESPONSE=$(api_call POST "/ingest/http" '{
    "device_id": "'$DEVICE_ID'",
    "metric": "soil_moisture",
    "value": '${READINGS[$i]}',
    "unit": "kPa",
    "ts": "'${TIMESTAMPS[$i]}'",
    "lat": 7.705,
    "lng": 8.205
  }' "$TOKEN")
  
  if echo "$INGEST_RESPONSE" | grep -q '"status":"ok"'; then
    log_info "  ✓ Reading $((i+1))/10: ${READINGS[$i]} kPa at ${TIMESTAMPS[$i]}"
  else
    log_warn "  ✗ Failed to ingest reading $((i+1)): $INGEST_RESPONSE"
  fi
done

log_info "✓ Sensor data ingestion complete"

# Summary
echo ""
echo "=========================================================================="
echo "✓ DEMO DATA CREATION SUCCESSFUL"
echo "=========================================================================="
echo ""
echo "Demo Credentials:"
echo "  Email:    $DEMO_EMAIL"
echo "  Password: $DEMO_PASS"
echo ""
echo "Resources Created:"
echo "  Tenant:       $DEMO_TENANT"
echo "  Farm ID:      $FARM_ID"
echo "  Field ID:     $PLOT_ID"
echo "  Crop ID:      $CROP_ID"
echo "  Sensor ID:    $DEVICE_ID"
echo "  Readings:     10 samples"
echo ""
echo "Next Steps:"
echo "  1. Open frontend: http://localhost:5173"
echo "  2. Login with demo credentials"
echo "  3. View farm, field, and sensor data"
echo "  4. Check map visualization"
echo ""
echo "API Test:"
echo "  curl -H 'Authorization: Bearer $TOKEN' \\"
echo "    'http://localhost:8000/api/v1/sensors/readings?from_ts=2025-11-27T00:00:00Z&to_ts=2025-11-27T23:59:59Z'"
echo ""
echo "=========================================================================="
