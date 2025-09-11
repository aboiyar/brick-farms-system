# backend/app/api/v1/tiles.py
from fastapi import APIRouter, Response, Depends, Path
from app.services.geoservice import generate_mvt
from app.api.deps import tenant_scoped_user

router = APIRouter(tags=["tiles"])

@router.get("/tiles/{z}/{x}/{y}/{layer}")
async def tiles(z: int = Path(...), x: int = Path(...), y: int = Path(...), layer: str = "plots", ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    mvt = await generate_mvt(str(token.tenant_id), z, x, y, layer=layer, db=db)
    return Response(content=mvt or b"", media_type="application/x-protobuf")

