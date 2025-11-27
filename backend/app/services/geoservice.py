# backend/app/services/geoservice.py
import math
import asyncio
from typing import Tuple
from app.db.session import AsyncSessionLocal
from app.config import settings
from redis import asyncio as aioredis
from sqlalchemy import text

_redis = None
async def get_redis():
    global _redis
    if not _redis:
        _redis = await aioredis.from_url(settings.REDIS_URL)
    return _redis

def tile_bounds(z:int, x:int, y:int):
    n = 2.0 ** z
    lon_deg_min = x / n * 360.0 - 180.0
    lat_rad_max = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg_max = lat_rad_max * 180.0 / math.pi

    lon_deg_max = (x + 1) / n * 360.0 - 180.0
    lat_rad_min = math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))
    lat_deg_min = lat_rad_min * 180.0 / math.pi
    return lon_deg_min, lat_deg_min, lon_deg_max, lat_deg_max

async def generate_mvt(tenant_id: str, z: int, x: int, y: int, layer: str="plots", db=None):
    try:
        r = await get_redis()
        key = f"tiles:{tenant_id}:{layer}:{z}:{x}:{y}"
        cached = await r.get(key)
        if cached:
            return cached
    except Exception:
        r = None

    if db is None:
        async with AsyncSessionLocal() as db:
            return await generate_mvt(tenant_id, z, x, y, layer, db=db)

    minx, miny, maxx, maxy = tile_bounds(z, x, y)
    if layer == "plots":
        sql = text("""
        WITH geomset AS (
          SELECT id, name, ST_AsMVTGeom(
            ST_Transform(geom, 3857),
            ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, 3857)
          ) AS geom, jsonb_build_object('name', name, 'area_ha', area_ha) AS props
          FROM fieldplot
          WHERE tenant_id = app_current_tenant()
            AND ST_Intersects(ST_Transform(geom,3857), ST_MakeEnvelope(:minx,:miny,:maxx,:maxy,3857))
          LIMIT 2000
        )
        SELECT ST_AsMVT(q, 'plots', 4096, 'geom') FROM (SELECT geom, props FROM geomset) q;
        """)
    elif layer == "assets":
        sql = text("""
        WITH geomset AS (
          SELECT id, name, ST_AsMVTGeom(
            ST_Transform(location, 3857),
            ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, 3857)
          ) AS geom, jsonb_build_object('name', name) AS props
          FROM sensordevice
          WHERE tenant_id = app_current_tenant()
            AND location IS NOT NULL
            AND ST_Intersects(ST_Transform(location,3857), ST_MakeEnvelope(:minx,:miny,:maxx,:maxy,3857))
          LIMIT 2000
        )
        SELECT ST_AsMVT(q, 'assets', 4096, 'geom') FROM (SELECT geom, props FROM geomset) q;
        """)
    else:
        raise ValueError("unknown layer")

    res = await db.execute(sql, {"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy})
    row = res.first()
    mvt_bytes = b""
    if row and row[0]:
        val = row[0]
        if hasattr(val, 'tobytes'):
            mvt_bytes = val.tobytes()
        else:
            mvt_bytes = val
    try:
        if r and mvt_bytes:
            await r.set(key, mvt_bytes, ex=60*60)
    except Exception:
        pass
    return mvt_bytes

# Tile invalidation helpers
def lonlat_to_tile(lon: float, lat: float, z: int) -> Tuple[int,int]:
    n = 2.0 ** z
    xtile = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + 1.0/math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def bbox_to_tile_range(minx: float, miny: float, maxx: float, maxy: float, z: int):
    x1,y1 = lonlat_to_tile(minx, miny, z)
    x2,y2 = lonlat_to_tile(maxx, maxy, z)
    return min(x1,x2), max(x1,x2), min(y1,y2), max(y1,y2)

def tile_key(tenant_id: str, layer: str, z: int, x: int, y: int) -> str:
    return f"tiles:{tenant_id}:{layer}:{z}:{x}:{y}"

async def invalidate_tiles_for_bbox(tenant_id: str, layer: str, minx: float, miny: float, maxx: float, maxy: float, min_zoom: int = 0, max_zoom: int = 14):
    r = await get_redis()
    max_zoom = min(max_zoom, 16)
    tasks = []
    for z in range(min_zoom, max_zoom + 1):
        x_min, x_max, y_min, y_max = bbox_to_tile_range(minx, miny, maxx, maxy, z)
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                key = tile_key(tenant_id, layer, z, x, y)
                tasks.append(r.delete(key))
    if tasks:
        await asyncio.gather(*tasks)

async def invalidate_tiles_for_tenant_layer(tenant_id: str, layer: str):
    r = await get_redis()
    pattern = f"tiles:{tenant_id}:{layer}:*"
    async for k in r.scan_iter(match=pattern):
        await r.delete(k)
    async with AsyncSessionLocal() as db:
        await db.execute(text("DELETE FROM tiles_cache WHERE tenant_id = :tid AND layer = :layer"), {"tid": tenant_id, "layer": layer})
        await db.commit()

