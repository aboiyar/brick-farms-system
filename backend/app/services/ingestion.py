from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import tenant_scoped_user

router = APIRouter(tags=["sensors"])

class IngestPayload(BaseModel):
    device_id: str
    metric: str
    value: float
    unit: str | None = None
    ts: str = Field(..., description="ISO8601 timestamp")
    lat: float | None = None
    lng: float | None = None

@router.post("/ingest/http")
async def ingest_http(p: IngestPayload, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    q = text("""
    INSERT INTO sensor_readings (tenant_id, device_id, metric, value, unit, timestamp, location)
    VALUES (:tid, :dev, :metric, :val, :unit, :ts,
            CASE WHEN :lat IS NULL THEN NULL
                 ELSE ST_SetSRID(ST_MakePoint(:lng,:lat),4326) END)
    """)
    await db.execute(q, {"tid": str(token.tenant_id), "dev": p.device_id, "metric": p.metric,
                         "val": p.value, "unit": p.unit, "ts": p.ts, "lat": p.lat, "lng": p.lng})
    await db.commit()
    return {"status": "ok"}
