from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from passlib.hash import bcrypt
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.tenant import Tenant
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token

router = APIRouter(tags=["auth"])

class SignupInput(BaseModel):
    tenant_name: str
    email: str
    password: str

@router.post("/signup")
async def signup(data: SignupInput, db: AsyncSession = Depends(get_db)):
    t_res = await db.execute(select(Tenant).where(Tenant.name == data.tenant_name))
    if t_res.scalar_one_or_none():
        raise HTTPException(400, "Tenant exists")
    tenant = Tenant(name=data.tenant_name)
    db.add(tenant); await db.flush()
    user = User(tenant_id=tenant.id, email=data.email, hashed_password=bcrypt.hash(data.password), role="owner")
    db.add(user); await db.commit()
    access = create_access_token(str(user.id), str(user.tenant_id), user.role)
    refresh = create_refresh_token(str(user.id), str(user.tenant_id))
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

class LoginInput(BaseModel):
    email: str
    password: str

@router.post("/token")
async def token(data: LoginInput, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.email == data.email))
    user = res.scalar_one_or_none()
    if not user or not bcrypt.verify(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    access = create_access_token(str(user.id), str(user.tenant_id), user.role)
    refresh = create_refresh_token(str(user.id), str(user.tenant_id))
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}
