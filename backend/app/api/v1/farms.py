from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import tenant_scoped_user
from app.models.farm import Farm

router = APIRouter(tags=["farms"])

class FarmIn(BaseModel):
    name: str
    country: str
    state: str | None = None
    lga: str | None = None

class FarmOut(FarmIn):
    id: str
    class Config: from_attributes = True

@router.post("/", response_model=FarmOut)
async def create_farm(data: FarmIn, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    farm = Farm(tenant_id=token.tenant_id, **data.model_dict())
    db.add(farm); await db.commit(); await db.refresh(farm)
    return farm

@router.get("/", response_model=list[FarmOut])
async def list_farms(ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    res = await db.execute(select(Farm))
    return list(res.scalars().all())
