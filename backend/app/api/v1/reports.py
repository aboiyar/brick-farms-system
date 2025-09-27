from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from app.api.deps import tenant_scoped_user
from app.schemas.reports import ForecastRequest, ForecastResponse, ForecastPoint, ActivitySummary, CarbonMetrics
from app.db.session import get_db
from sqlalchemy import text
from datetime import datetime, timedelta
import io, csv
from typing import List

# statsmodels for simple Holt-Winters forecasting
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
except Exception:
    ExponentialSmoothing = None

router = APIRouter(tags=["reports"])


@router.get('/forecast', response_model=List[ForecastResponse])
async def forecast(farm_id: str | None = None, plot_id: str | None = None, crop: str | None = None, horizon_days: int = 90, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    # Query recent yields for the plot/farm and compute a Holt-Winters forecast
    params = {"tid": token.tenant_id, "farm_id": farm_id, "plot_id": plot_id}
    q = "SELECT ts, yield_kg FROM yields WHERE tenant_id = :tid"
    if plot_id:
        q += " AND plot_id = :plot_id"
    elif farm_id:
        q += " AND farm_id = :farm_id"
    q += " ORDER BY ts DESC LIMIT 365"
    res = await db.execute(text(q), params)
    rows = res.fetchall()
    # extract a univariate time series sorted by ts (oldest -> newest)
    series = []
    for r in reversed(rows):
        try:
            series.append(float(r.yield_kg))
        except Exception:
            continue

    now = datetime.utcnow()
    points = []

    if ExponentialSmoothing and len(series) >= 3:
        # use additive seasonal model with seasonality of 7 days if we have enough resolution
        season = 7 if len(series) >= 14 else None
        try:
            model = ExponentialSmoothing(series, trend='add', seasonal='add' if season else None, seasonal_periods=season)
            fit = model.fit(optimized=True)
            preds = fit.forecast(horizon_days)
            for i in range(horizon_days):
                d = now + timedelta(days=i)
                val = float(preds[i]) if i < len(preds) else 0.0
                points.append(ForecastPoint(date=d, yield_kg=max(0.0, val)))
        except Exception:
            # fallback to simple average per-sample projection
            avg = sum(series) / len(series) if series else 0.0
            for i in range(horizon_days):
                d = now + timedelta(days=i)
                points.append(ForecastPoint(date=d, yield_kg=max(0.0, avg / max(1, horizon_days))))
    else:
        # not enough data or dependency missing - fallback to simple average
        avg = sum(series) / len(series) if series else 0.0
        for i in range(horizon_days):
            d = now + timedelta(days=i)
            points.append(ForecastPoint(date=d, yield_kg=max(0.0, avg / max(1, horizon_days))))
    resp = ForecastResponse(plot_id=plot_id, crop=crop, points=points)
    return [resp]


@router.get('/activity', response_model=ActivitySummary)
async def activity(farm_id: str | None = None, from_ts: str | None = None, to_ts: str | None = None, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    params = {"tid": token.tenant_id, "farm_id": farm_id, "from_ts": from_ts, "to_ts": to_ts}
    q = "SELECT action, COUNT(*) as cnt FROM activity WHERE tenant_id = :tid"
    if farm_id:
        q += " AND farm_id = :farm_id"
    if from_ts:
        q += " AND ts >= :from_ts"
    if to_ts:
        q += " AND ts <= :to_ts"
    q += " GROUP BY action"
    res = await db.execute(text(q), params)
    rows = res.fetchall()
    counts = {r.action: int(r.cnt) for r in rows} if rows else {}
    return ActivitySummary(farm_id=farm_id, activity_counts=counts)


@router.get('/carbon', response_model=CarbonMetrics)
async def carbon(farm_id: str | None = None, from_ts: str | None = None, to_ts: str | None = None, ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    # simple carbon estimate: assign factors per activity
    params = {"tid": token.tenant_id, "farm_id": farm_id, "from_ts": from_ts, "to_ts": to_ts}
    q = "SELECT action, COUNT(*) as cnt FROM activity WHERE tenant_id = :tid"
    if farm_id:
        q += " AND farm_id = :farm_id"
    if from_ts:
        q += " AND ts >= :from_ts"
    if to_ts:
        q += " AND ts <= :to_ts"
    q += " GROUP BY action"
    res = await db.execute(text(q), params)
    rows = res.fetchall()
    # simple factors (tonnes CO2e per activity)
    factors = {"irrigation": 0.001, "planting": 0.01, "harvest": 0.005, "maintenance": 0.002}
    total = 0.0
    for r in rows:
        f = factors.get(r.action, 0.001)
        total += f * int(r.cnt)
    return CarbonMetrics(farm_id=farm_id, co2e_tonnes=total)


def _generate_csv(rows: List[dict]):
    buf = io.StringIO()
    if not rows:
        return buf.getvalue().encode()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return buf.getvalue().encode()


@router.get('/export.csv')
async def export_csv(ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    # For demo, export activity summary as CSV
    # derive CSV from activity summary
    q = "SELECT action, COUNT(*) as cnt FROM activity WHERE tenant_id = :tid GROUP BY action"
    res = await db.execute(text(q), {"tid": token.tenant_id})
    rows = []
    for r in res.fetchall():
        rows.append({"metric": r.action, "count": int(r.cnt)})
    data = _generate_csv(rows)
    return StreamingResponse(io.BytesIO(data), media_type='text/csv', headers={"Content-Disposition": "attachment; filename=report.csv"})


@router.get('/export.pdf')
async def export_pdf(ctx=Depends(tenant_scoped_user)):
    token, db = ctx
    # Try to generate a simple PDF using reportlab if available
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
    except Exception:
        raise HTTPException(status_code=503, detail="PDF generation dependency not available")

    # Fetch activity aggregates for the tenant
    q = "SELECT action, COUNT(*) as cnt FROM activity WHERE tenant_id = :tid GROUP BY action"
    res = await db.execute(text(q), {"tid": token.tenant_id})
    rows = res.fetchall() if res is not None else []

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # Header
    c.setFont('Helvetica-Bold', 16)
    c.drawString(72, height - 72, 'BrickFarm Activity Report')
    c.setFont('Helvetica', 10)
    c.drawString(72, height - 90, f'Tenant: {token.tenant_id}')
    c.drawString(72, height - 106, f'Date: {datetime.utcnow().isoformat()}')

    # Table
    y = height - 140
    c.setFont('Helvetica-Bold', 12)
    c.drawString(72, y, 'Activity')
    c.drawString(300, y, 'Count')
    y -= 18
    c.setFont('Helvetica', 11)
    if not rows:
        c.drawString(72, y, 'No activity data available')
    else:
        for r in rows:
            c.drawString(72, y, str(r.action))
            c.drawString(300, y, str(int(r.cnt)))
            y -= 16
            if y < 72:
                c.showPage()
                y = height - 72

    c.showPage()
    c.save()
    buf.seek(0)
    return StreamingResponse(buf, media_type='application/pdf', headers={"Content-Disposition": "attachment; filename=report.pdf"})
