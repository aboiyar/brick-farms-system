from fastapi import Depends, HTTPException, status, Request
from app.core.security import TokenData, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db

# We push tenant_id into a Postgres local setting for RLS policies to use
async def set_tenant_context(request: Request,
                             db: AsyncSession = Depends(get_db),
                             token: TokenData = Depends(get_current_user)):
    if not token.tenant_id:
        raise HTTPException(status_code=403, detail="Tenant scope required")
    await db.execute(text("SELECT set_config('app.tenant_id', :tid, true)"), {"tid": str(token.tenant_id)})
    # Note: connection is scoped to transaction; ensure all queries happen after this dependency
    return token
