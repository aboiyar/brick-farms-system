# backend/app/api/v1/tasks.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.api.deps import tenant_scoped_user
from app.services.files import put_object, presign_get_url
import uuid, json
from geoalchemy2.shape import to_shape
from datetime import datetime

router = APIRouter(tags=["tasks"])

class TaskCreateIn(BaseModel):
    workorder_id: Optional[str] = None
    title: str
    assignee_id: Optional[str] = None
    due_at: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    gps_accuracy_m: Optional[float] = None
    meta: dict = {}

class ObservationCreateIn(BaseModel):
    plot_id: Optional[str] = None
    task_id: Optional[str] = None
    notes: Optional[str] = None
    metrics: dict = {}
    lat: Optional[float] = None
    lng: Optional[float] = None

@router.post("/tasks")
async def create_task(payload: TaskCreateIn, ctx=Depends(tenant_scoped_user)):
    token, db: AsyncSession = ctx
    if payload.lat is not None and payload.lng is not None:
        q = text("""
        INSERT INTO task (tenant_id, workorder_id, title, assignee_id, status, location, gps_accuracy_m, created_at, due_at, meta)
        VALUES (:tid, :wo, :title, :assignee, 'pending', ST_SetSRID(ST_MakePoint(:lng,:lat),4326), :gps, now(), :due, :meta)
        RETURNING id
        """)
        params = {"tid": str(token.tenant_id), "wo": payload.workorder_id, "title": payload.title,
                  "assignee": payload.assignee_id, "gps": payload.gps_accuracy_m, "due": payload.due_at,
                  "lat": payload.lat, "lng": payload.lng, "meta": json.dumps(payload.meta)}
    else:
        q = text("""
        INSERT INTO task (tenant_id, workorder_id, title, assignee_id, status, created_at, due_at, meta)
        VALUES (:tid, :wo, :title, :assignee, 'pending', now(), :due, :meta)
        RETURNING id
        """)
        params = {"tid": str(token.tenant_id), "wo": payload.workorder_id, "title": payload.title,
                  "assignee": payload.assignee_id, "due": payload.due_at, "meta": json.dumps(payload.meta)}
    res = await db.execute(q, params)
    row = res.first()
    await db.commit()
    return {"id": str(row.id)}

@router.post("/observations")
async def create_observation_json(payload: ObservationCreateIn, ctx=Depends(tenant_scoped_user)):
    token, db: AsyncSession = ctx
    q = text("""
    INSERT INTO observation (tenant_id, plot_id, task_id, observer_id, ts, notes, metrics, location)
    VALUES (:tid, :plot, :task, :obs, now(), :notes::text, :metrics::jsonb,
            CASE WHEN :lat IS NULL THEN NULL ELSE ST_SetSRID(ST_MakePoint(:lng,:lat),4326) END)
    RETURNING id
    """)
    res = await db.execute(q, {"tid": str(token.tenant_id), "plot": payload.plot_id, "task": payload.task_id,
                               "obs": token.sub, "notes": payload.notes or "", "metrics": json.dumps(payload.metrics),
                               "lat": payload.lat, "lng": payload.lng})
    row = res.first(); await db.commit()
    return {"id": str(row.id)}

@router.post("/observations/multipart")
async def create_observation_multipart(
    plot_id: Optional[str] = Form(None),
    task_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    metrics: Optional[str] = Form("{}"),
    lat: Optional[float] = Form(None),
    lng: Optional[float] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    ctx=Depends(tenant_scoped_user)
):
    token, db: AsyncSession = ctx
    metrics_obj = json.loads(metrics or "{}")
    q = text("""
    INSERT INTO observation (tenant_id, plot_id, task_id, observer_id, ts, notes, metrics, location)
    VALUES (:tid, :plot, :task, :obs, now(), :notes::text, :metrics::jsonb,
            CASE WHEN :lat IS NULL THEN NULL ELSE ST_SetSRID(ST_MakePoint(:lng,:lat),4326) END)
    RETURNING id
    """)
    res = await db.execute(q, {"tid": str(token.tenant_id), "plot": plot_id, "task": task_id,
                               "obs": token.sub, "notes": notes or "", "metrics": json.dumps(metrics_obj),
                               "lat": lat, "lng": lng})
    row = res.first()
    if not row:
        raise HTTPException(500, "Failed to create observation")
    obs_id = str(row.id)
    await db.commit()

    uploaded = []
    if files:
        for f in files:
            key = f"{token.tenant_id}/observations/{obs_id}/{uuid.uuid4().hex}-{f.filename}"
            body = await f.read()
            put_object(key, body, content_type=f.content_type or "application/octet-stream")
            get_url = presign_get_url(key)
            q2 = text("INSERT INTO photo_report (tenant_id, observation_id, url, thumb_url, exif, ts) VALUES (:tid, :obs, :url, NULL, :exif::jsonb, now()) RETURNING id")
            res2 = await db.execute(q2, {"tid": str(token.tenant_id), "obs": obs_id, "url": key, "exif": json.dumps({})})
            row2 = res2.first()
            uploaded.append({"url": key, "id": str(row2.id), "get_url": get_url})
        await db.commit()

    return {"observation_id": obs_id, "photos": uploaded}

# GET tasks with filters
from typing import List, Optional
from uuid import UUID
from app.api.v1.schemas.task import TaskOut as TaskOutSchema
from app.models.tasking import Task as TaskModel, Task as TaskEnum
from sqlalchemy import text as sql_text

@router.get("/tasks", response_model=List[dict])
async def list_tasks(
    status: Optional[str] = Query(None),
    assignee_id: Optional[UUID] = Query(None),
    bbox: Optional[str] = Query(None, description="minx,miny,maxx,maxy"),
    ctx=Depends(tenant_scoped_user)
):
    token, db = ctx
    query = "SELECT id, farm_id, title as name, description, status, assignee_id, due_at, created_at, updated_at, ST_AsGeoJSON(location) as location FROM task WHERE tenant_id = app_current_tenant()"
    params = {}
    if status:
        query += " AND status = :status"
        params["status"] = status
    if assignee_id:
        query += " AND assignee_id = :assignee_id"
        params["assignee_id"] = str(assignee_id)
    if bbox:
        try:
            minx,miny,maxx,maxy = [float(x) for x in bbox.split(",")]
            query += " AND location IS NOT NULL AND ST_Within(location, ST_MakeEnvelope(:minx,:miny,:maxx,:maxy,4326))"
            params.update({"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy})
        except Exception:
            raise HTTPException(400, "Invalid bbox format")
    query += " ORDER BY created_at DESC LIMIT 1000"
    res = await db.execute(sql_text(query), params)
    rows = res.fetchall()
    out = []
    for r in rows:
        rec = dict(r._mapping)
        loc = rec.get("location")
        rec["location"] = json.loads(loc) if loc else None
        out.append(rec)
    return out
