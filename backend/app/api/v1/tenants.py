from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import tenant_scoped_user
from app.models.tenant import Tenant

router = APIRouter(tags=["tenants"])

class TenantOut(BaseModel):
    id: str
    name: str
    plan: str
    class Config: from_attributes = True

@router.get("/me", response_model=TenantOut)
async def my_tenant(ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    res = await db.execute(select(Tenant).where(Tenant.id == token.tenant_id))
    return res.scalar_one()
