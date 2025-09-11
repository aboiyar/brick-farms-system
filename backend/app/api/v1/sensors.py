from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.api.deps import tenant_scoped_user
from app.models.sensor import SensorDevice

router = APIRouter(tags=["sensors"])

class DeviceIn(BaseModel):
    farm_id: str
    plot_id: str | None = None
    name: str
    protocol: str = "http"
    api_key: str

class DeviceOut(DeviceIn):
    id: str
    class Config: from_attributes = True

@router.post("/devices", response_model=DeviceOut)
async def create_device(d: DeviceIn, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    dev = SensorDevice(tenant_id=token.tenant_id, **d.model_dump())
    db.add(dev); await db.commit(); await db.refresh(dev)
    return dev

@router.get("/readings")
async def readings(from_ts: str, to_ts: str, metric: str | None = None, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    q = """
    SELECT device_id, metric, unit,
           time_bucket('1 hour', timestamp) AS ts,
           avg(value) AS value
    FROM sensor_readings
    WHERE tenant_id = app_current_tenant()
      AND timestamp BETWEEN :from_ts AND :to_ts
      AND (:metric IS NULL OR metric = :metric)
    GROUP BY device_id, metric, unit, ts
    ORDER BY ts ASC
    """
    res = await db.execute(text(q), {"from_ts": from_ts, "to_ts": to_ts, "metric": metric})
    rows = [dict(r._mapping) for r in res]
    return rows
