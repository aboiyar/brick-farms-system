# backend/app/api/v1/uploads.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.services.files import presign_put_url, presign_get_url
from app.api.deps import tenant_scoped_user
from uuid import uuid4
from sqlalchemy import text

router = APIRouter(tags=["uploads"])

class PresignRequest(BaseModel):
    filename: str
    content_type: str
    purpose: str = "observation"

class PresignResponse(BaseModel):
    upload_url: str
    key: str

@router.post("/presign", response_model=PresignResponse)
async def presign(req: PresignRequest, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    ext = req.filename.split(".")[-1] if "." in req.filename else "bin"
    key = f"{token.tenant_id}/{req.purpose}/{uuid4().hex}.{ext}"
    upload_url = presign_put_url(key, expires=3600)
    return {"upload_url": upload_url, "key": key}

class RegisterUploadIn(BaseModel):
    observation_id: str | None = None
    task_id: str | None = None
    key: str
    filename: str | None = None
    exif: dict | None = None

@router.post("/register")
async def register_upload(payload: RegisterUploadIn, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    q = text("""
    INSERT INTO photo_report (tenant_id, observation_id, url, thumb_url, exif, ts)
    VALUES (:tid, :obs, :url, NULL, :exif::jsonb, now())
    RETURNING id
    """)
    exif_json = payload.exif or {}
    res = await db.execute(q, {"tid": str(token.tenant_id), "obs": payload.observation_id, "url": payload.key, "exif": exif_json})
    row = res.first()
    await db.commit()
    photo_id = str(row.id)
    # enqueue celery task if available
    try:
        from app.celery_app import celery_app
        celery_app.send_task("tasks.process_image_task", args=[str(token.tenant_id), payload.key, photo_id])
    except Exception:
        pass
    get_url = presign_get_url(payload.key, expires=3600)
    return {"photo_report_id": photo_id, "get_url": get_url}
