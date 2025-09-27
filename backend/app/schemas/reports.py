from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date, datetime
from uuid import UUID


class ForecastRequest(BaseModel):
    farm_id: Optional[UUID] = None
    plot_id: Optional[UUID] = None
    crop: Optional[str] = None
    horizon_days: int = 90


class ForecastPoint(BaseModel):
    date: datetime
    yield_kg: float


class ForecastResponse(BaseModel):
    plot_id: Optional[UUID]
    crop: Optional[str]
    points: List[ForecastPoint]


class ActivitySummary(BaseModel):
    farm_id: Optional[UUID]
    activity_counts: Dict[str, int]


class CarbonMetrics(BaseModel):
    farm_id: Optional[UUID]
    co2e_tonnes: float
