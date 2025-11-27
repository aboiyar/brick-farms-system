# 🚀 BRICKFARM LAUNCH GUIDE

**Status:** Ready for Demo Launch (6 hours to 7:00 AM)  
**Updated:** November 27, 2025  
**Target:** Stakeholder demonstration of fully functional BrickFarm platform

---

## QUICK START (5 MINUTES)

### Prerequisites
- **Docker & Docker Compose** (for Postgres 14 + PostGIS + Redis)
- **Python 3.11+** (for FastAPI backend)
- **Node.js + Yarn/npm** (for React frontend)

### One-Command Launch
```bash
cd /opt/brickfarm
./launch.sh
```

**That's it!** The script will:
1. ✅ Start Docker services (Postgres + Redis)
2. ✅ Setup Python venv and install dependencies
3. ✅ Run database migrations
4. ✅ Start FastAPI backend on `http://localhost:8000`
5. ✅ Install frontend deps and start Vite on `http://localhost:5173`

---

## WHAT YOU'LL SEE

### Console Output
```
[INFO] Starting Docker services (Postgres + Redis)...
[INFO] ✓ Postgres is ready
[INFO] ✓ Redis is ready
[INFO] Setting up Python environment for backend...
[INFO] ✓ Python environment ready
[INFO] Running database migrations...
[INFO] ✓ Migrations complete
[INFO] Setting up frontend environment...
[INFO] ✓ Frontend environment ready
[INFO] Starting backend in background...
[INFO] Backend PID: 12345
[INFO] ✓ Backend is responding
[INFO]
[INFO] ======================================================================
[INFO] ✓ BrickFarm is running!
[INFO] ======================================================================
[INFO]
[INFO] Frontend:  http://localhost:5173
[INFO] Backend:   http://localhost:8000
[INFO] API Docs:  http://localhost:8000/docs
[INFO] DB:        localhost:5433
[INFO]
```

### Open Your Browser
1. Frontend: **http://localhost:5173** → You'll see the BrickFarm login page
2. Backend Docs: **http://localhost:8000/docs** → Interactive API documentation

---

## DEMO WALKTHROUGH (7:00 AM - STAKEHOLDER DEMO)

### Step 1: Signup (Create a New Tenant)
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{
    "tenant_name": "BrickServers Farm NG",
    "email": "demo@brickfarm.ng",
    "password": "Demo123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Copy the `access_token` for subsequent calls.

### Step 2: Create a Farm
```bash
TOKEN="<your_access_token_from_step_1>"

curl -X POST http://localhost:8000/api/v1/farms/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Gboko Demo Farm",
    "country": "NG",
    "state": "Benue",
    "lga": "Gboko"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Gboko Demo Farm",
  "country": "NG",
  "state": "Benue",
  "lga": "Gboko"
}
```

Copy the `farm_id` for the next step.

### Step 3: Create a Field/Plot with Map
```bash
FARM_ID="<farm_id_from_step_2>"

curl -X POST http://localhost:8000/api/v1/fields/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "farm_id": "'$FARM_ID'",
    "name": "Plot A - Maize Field",
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
  }'
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440111",
  "name": "Plot A - Maize Field",
  "area_ha": 0.112
}
```

### Step 4: Create a Crop
```bash
curl -X POST http://localhost:8000/api/v1/crops/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "category": "crop",
    "common_name": "Maize (Corn)",
    "scientific_name": "Zea mays",
    "descriptors": {
      "days_to_maturity": {"required": true, "unit": "days"},
      "planting_depth": {"required": true, "unit": "cm"}
    }
  }'
```

### Step 5: Create a Sensor Device
```bash
curl -X POST http://localhost:8000/api/v1/sensors/devices \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "farm_id": "'$FARM_ID'",
    "plot_id": "'<plot_id_from_step_3>'",
    "name": "Soil Moisture Sensor #1",
    "protocol": "http",
    "api_key": "sensor_key_12345"
  }'
```

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440222",
  "farm_id": "550e8400-e29b-41d4-a716-446655440000",
  "plot_id": "660e8400-e29b-41d4-a716-446655440111",
  "name": "Soil Moisture Sensor #1",
  "protocol": "http",
  "api_key": "sensor_key_12345"
}
```

### Step 6: Ingest Sensor Data
```bash
DEVICE_ID="<device_id_from_step_5>"

curl -X POST http://localhost:8000/api/v1/ingest/http \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": "'$DEVICE_ID'",
    "metric": "soil_moisture",
    "value": 19.3,
    "unit": "kPa",
    "ts": "2025-11-27T14:30:00Z",
    "lat": 7.705,
    "lng": 8.205
  }'
```

### Step 7: Query Sensor Readings
```bash
curl -X GET "http://localhost:8000/api/v1/sensors/readings?from_ts=2025-11-27T00:00:00Z&to_ts=2025-11-27T23:59:59Z&metric=soil_moisture" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
[
  {
    "device_id": "770e8400-e29b-41d4-a716-446655440222",
    "metric": "soil_moisture",
    "unit": "kPa",
    "ts": "2025-11-27T14:00:00+00:00",
    "value": 19.3
  }
]
```

### Step 8: Check Frontend
Open **http://localhost:5173** in your browser:
- Login with `demo@brickfarm.ng` / `Demo123!`
- View the map with your farm and field plot
- See sensor readings displayed in real-time

---

## TROUBLESHOOTING

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

### Database Connection Refused
```bash
# Verify Docker services are running
docker-compose ps

# Restart services
docker-compose down
docker-compose up -d db redis
```

### Python Venv Issues
```bash
# Remove existing venv and recreate
rm -rf backend/.venv
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend Doesn't Connect to Backend
```bash
# Check the API endpoint in frontend/.env.local
cat frontend-web/.env.local

# Should say: VITE_API_URL=http://localhost:8000/api/v1
# Update if needed and restart the frontend dev server
```

### Migrations Fail
```bash
# Check Postgres is running
docker-compose exec db pg_isready -U brickfarm

# Reset database (⚠️ WARNING: DELETES ALL DATA)
docker-compose down -v
docker-compose up -d db
# Then re-run: alembic upgrade head
```

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    BRICKFARM STACK                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  FRONTEND (Port 5173)                                       │
│  ├─ React 18.2 + Vite                                       │
│  ├─ OpenLayers for maps                                     │
│  ├─ AuthContext for JWT tokens                              │
│  └─ Responsive UI (mobile-friendly)                         │
│                        │                                     │
│                        ↓ (HTTP/REST)                         │
│  BACKEND API (Port 8000)                                    │
│  ├─ FastAPI + Uvicorn                                       │
│  ├─ 8+ routers (auth, farms, fields, crops, sensors, etc) │
│  ├─ JWT authentication                                      │
│  ├─ Multi-tenant architecture (RLS)                         │
│  └─ Async SQLAlchemy                                        │
│                        │                                     │
│                        ↓ (PostgreSQL)                        │
│  DATABASE (Port 5433)                                       │
│  ├─ Postgres 14                                             │
│  ├─ PostGIS extension (geospatial)                          │
│  ├─ TimescaleDB extension (time-series)                     │
│  ├─ 13 tables with RLS policies                             │
│  └─ Hypertable for sensor_readings                          │
│                                                               │
│  CACHE (Port 6380)                                          │
│  ├─ Redis 7                                                 │
│  ├─ For celery tasks (future)                               │
│  └─ For session caching (future)                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## KEY FEATURES READY FOR DEMO

### ✅ Authentication
- Signup: Create new tenant + owner user
- Login: JWT token-based authentication
- Token expiry: 15 min access + 30-day refresh

### ✅ Multi-Tenancy
- Each tenant isolated via RLS policies
- `app_current_tenant()` enforces data isolation
- Automatic tenant scope in all queries

### ✅ Geospatial
- PostGIS for polygon storage (fields)
- Vector queries on field boundaries
- Distance calculations built-in

### ✅ Time-Series Sensor Data
- TimescaleDB hypertable for sensor_readings
- HTTP ingestion endpoint: `/api/v1/ingest/http`
- Bucketed queries (time_bucket) for aggregation

### ✅ Finance Module
- Double-entry accounting scaffolding
- Account types: asset, liability, equity, income, expense
- Ledger entries with currency support

### ✅ Reports
- Sensor data aggregation by time + metric
- Farm/field-level summaries
- Financial reports (stub)

### ✅ Audit Logging
- Every mutation tracked in AuditLog table
- Actor ID, action, entity, timestamp

---

## NEXT STEPS (AFTER 7 AM DEMO)

### Phase 1: Production Hardening
- [ ] Add HTTPS (Let's Encrypt + Nginx)
- [ ] Secure JWT_SECRET via secrets manager
- [ ] Enable database backups (nightly)
- [ ] Add request rate limiting

### Phase 2: Mobile App
- React Native app in `/mobile/BrickFarmMobile/`
- Same API client as web
- Offline-first architecture (future)

### Phase 3: Advanced Features
- [ ] Vector tile generation (MVT) for large maps
- [ ] MQTT/CoAP gateway for IoT sensor integration
- [ ] Government APIs integration (read-only views)
- [ ] i18n (Hausa, Yoruba, Tiv translations)
- [ ] Task/WorkOrder management system
- [ ] Photo uploads + image processing (via S3/MinIO)

### Phase 4: Scaling
- [ ] Container orchestration (K8s or Docker Swarm)
- [ ] Horizontal scaling for API tier
- [ ] Read replicas for analytics queries
- [ ] Celery workers for background jobs
- [ ] WebSocket support for real-time notifications

---

## SUPPORT & DEBUGGING

### View Live Logs
```bash
# Backend logs
tail -f /tmp/brickfarm-backend.log

# Frontend build output
# Check browser console (F12 → Console tab)

# Database logs
docker-compose logs db
```

### Database Access
```bash
# Connect directly to Postgres
psql -h 127.0.0.1 -p 5433 -U brickfarm -d brickfarm

# Useful queries:
SELECT * FROM tenant;
SELECT * FROM "user";
SELECT * FROM farm;
SELECT * FROM sensor_readings LIMIT 10;
```

### API Documentation
**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

---

## FINAL CHECKLIST FOR 7 AM DEMO

- [ ] Run `./launch.sh` and verify all services start
- [ ] Frontend loads at http://localhost:5173
- [ ] Backend API docs at http://localhost:8000/docs
- [ ] Can signup and create a tenant
- [ ] Can create a farm and field with geolocation
- [ ] Sensor data ingestion works
- [ ] Map displays fields correctly
- [ ] Logout and login again (JWT token persistence)
- [ ] Show audit logs of all actions
- [ ] Demonstrate multi-tenancy (create another tenant, verify isolation)

---

## CONTACT

For questions or issues, check:
1. Backend logs: `/tmp/brickfarm-backend.log`
2. Frontend console: Browser DevTools (F12)
3. Database: `psql -h 127.0.0.1 -p 5433 -U brickfarm`
4. This guide for troubleshooting

**Good luck with the demo! 🚀**
