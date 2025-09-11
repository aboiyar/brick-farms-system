# backend/app/api/v1/fields.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.deps import tenant_scoped_user
from app.services.geoservice import invalidate_tiles_for_bbox
import json, re

router = APIRouter(tags=["fields"])

class FieldIn(BaseModel):
    farm_id: str
    name: str
    geom_geojson: dict = Field(..., description="Polygon GeoJSON")

class FieldOut(BaseModel):
    id: str
    name: str
    area_ha: float | None
    class Config:
        from_attributes = True

@router.post("/", response_model=FieldOut)
async def create_field(data: FieldIn, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    geojson_str = json.dumps(data.geom_geojson)
    q = text("""
    INSERT INTO fieldplot (tenant_id, farm_id, name, geom, area_ha)
    VALUES (:tid, :fid, :name, ST_SetSRID(ST_GeomFromGeoJSON(:geojson),4326),
            ST_Area(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(:geojson),4326), 6933))/10000.0)
    RETURNING id, name, area_ha, ST_Extent(geom) as extent
    """)
    res = await db.execute(q, {"tid": str(token.tenant_id), "fid": data.farm_id, "name": data.name, "geojson": geojson_str})
    row = res.first()
    if not row:
        raise HTTPException(400, "Insert failed")
    await db.commit()

    extent_text = row.extent
    if extent_text:
        m = re.match(r"BOX\(([-\d\.]+) ([-\d\.]+),([-\d\.]+) ([-\d\.]+)\)", extent_text)
        if m:
            minx, miny, maxx, maxy = map(float, m.groups())
            try:
                await invalidate_tiles_for_bbox(str(token.tenant_id), "plots", minx, miny, maxx, maxy, min_zoom=0, max_zoom=14)
            except Exception:
                pass

    return {"id": str(row.id), "name": row.name, "area_ha": float(row.area_ha or 0)}

@router.put("/{field_id}", response_model=FieldOut)
async def update_field(field_id: str, data: FieldIn, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    # old extent
    res_old = await db.execute(text("SELECT ST_Extent(geom) as extent FROM fieldplot WHERE id = :fid AND tenant_id = app_current_tenant()"), {"fid": field_id})
    old_row = res_old.first()
    old_extent = old_row.extent if old_row else None

    geojson_str = json.dumps(data.geom_geojson)
    q = text("""
    UPDATE fieldplot SET name = :name, geom = ST_SetSRID(ST_GeomFromGeoJSON(:geojson),4326),
      area_ha = ST_Area(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(:geojson),4326),6933))/10000.0
    WHERE id = :fid AND tenant_id = app_current_tenant()
    RETURNING id, name, area_ha, ST_Extent(geom) as extent
    """)
    res = await db.execute(q, {"fid": field_id, "name": data.name, "geojson": geojson_str})
    row = res.first()
    if not row:
        raise HTTPException(404, "Field not found")
    await db.commit()

    def parse_extent(ext):
        if not ext: return None
        m = re.match(r"BOX\(([-\d\.]+) ([-\d\.]+),([-\d\.]+) ([-\d\.]+)\)", ext)
        if m: return tuple(map(float, m.groups()))
        return None

    old_parsed = parse_extent(old_extent)
    new_parsed = parse_extent(row.extent)
    try:
        if old_parsed:
            await invalidate_tiles_for_bbox(str(token.tenant_id), "plots", *old_parsed, min_zoom=0, max_zoom=14)
        if new_parsed:
            await invalidate_tiles_for_bbox(str(token.tenant_id), "plots", *new_parsed, min_zoom=0, max_zoom=14)
    except Exception:
        pass

    return {"id": str(row.id), "name": row.name, "area_ha": float(row.area_ha or 0)}

@router.delete("/{field_id}")
async def delete_field(field_id: str, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    res = await db.execute(text("SELECT ST_Extent(geom) as extent FROM fieldplot WHERE id = :fid AND tenant_id = app_current_tenant()"), {"fid": field_id})
    row = res.first()
    old_extent = row.extent if row else None
    await db.execute(text("DELETE FROM fieldplot WHERE id = :fid AND tenant_id = app_current_tenant()"), {"fid": field_id})
    await db.commit()
    if old_extent:
        import re
        m = re.match(r"BOX\(([-\d\.]+) ([-\d\.]+),([-\d\.]+) ([-\d\.]+)\)", old_extent)
        if m:
            minx,miny,maxx,maxy = map(float, m.groups())
            try:
                await invalidate_tiles_for_bbox(str(token.tenant_id), "plots", minx, miny, maxx, maxy, min_zoom=0, max_zoom=14)
            except Exception:
                pass
    return {"status":"deleted"}
