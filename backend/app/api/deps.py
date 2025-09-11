from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user, TokenData
from app.core.tenancy import set_tenant_context

async def tenant_scoped_user(token: TokenData = Depends(set_tenant_context),
                             db: AsyncSession = Depends(get_db)):
    return token, db
