# backend/app/tasks.py
from app.celery_app import celery_app
from app.services.files import s3_client
from PIL import Image
import io, os, re, asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text
from app.services.geoservice import invalidate_tiles_for_tenant_layer

@celery_app.task(name="tasks.process_image_task")
def process_image_task(tenant_id: str, s3_key: str, photo_report_id: str):
    cl = s3_client()
    bucket = os.environ.get("S3_BUCKET", "brickfarm")
    try:
        resp = cl.get_object(Bucket=bucket, Key=s3_key)
        body = resp["Body"].read()
    except Exception as e:
        # Could not read object
        return {"error": str(e)}

    thumbs = {}
    try:
        img = Image.open(io.BytesIO(body))
        sizes = {"medium": (512,512), "small": (128,128)}
        for tag, size in sizes.items():
            im = img.copy()
            im.thumbnail(size, Image.ANTIALIAS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=85)
            buf.seek(0)
            thumb_key = f"thumbs/{s3_key}"
            cl.put_object(Bucket=bucket, Key=thumb_key, Body=buf, ContentType="image/jpeg")
            thumbs[tag] = thumb_key
    except Exception:
        thumbs = {}

    async def update_db():
        async with AsyncSessionLocal() as db:
            await db.execute(text("UPDATE photo_report SET thumb_url = :thumb, exif = :exif WHERE id = :id"),
                             {"thumb": thumbs.get("medium"), "exif": {}, "id": photo_report_id})
            await db.commit()
            # find observation and then fieldplot extent to invalidate tiles
            res = await db.execute(text("SELECT observation_id FROM photo_report WHERE id = :id"), {"id": photo_report_id})
            r = res.first()
            if r and r.observation_id:
                obs_id = r.observation_id
                r2 = await db.execute(text("SELECT plot_id FROM observation WHERE id = :oid"), {"oid": obs_id})
                r2row = r2.first()
                if r2row and r2row.plot_id:
                    r3 = await db.execute(text("SELECT ST_Extent(geom) as extent FROM fieldplot WHERE id = :pid AND tenant_id = :tid"), {"pid": r2row.plot_id, "tid": tenant_id})
                    r3row = r3.first()
                    if r3row and r3row.extent:
                        m = re.match(r"BOX\(([-\d\.]+) ([-\d\.]+),([-\d\.]+) ([-\d\.]+)\)", r3row.extent)
                        if m:
                            minx, miny, maxx, maxy = map(float, m.groups())
                            await invalidate_tiles_for_tenant_layer(tenant_id, "plots")
    try:
        asyncio.run(update_db())
    except Exception:
        pass

    return {"thumbs": thumbs}
