from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import tenant_scoped_user
from app.models.crop import Crop, Variety

router = APIRouter(tags=["crops"])

class CropIn(BaseModel):
    category: str
    common_name: str
    scientific_name: str | None = None
    descriptors: dict = {}

class CropOut(CropIn):
    id: str
    class Config: from_attributes = True

@router.post("/", response_model=CropOut)
async def create_crop(data: CropIn, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    crop = Crop(tenant_id=token.tenant_id, **data.model_dump())
    db.add(crop); await db.commit(); await db.refresh(crop)
    return crop

@router.get("/", response_model=list[CropOut])
async def list_crops(ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    res = await db.execute(select(Crop))
    return list(res.scalars().all())
