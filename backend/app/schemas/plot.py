from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class GeometryGeoJSON(BaseModel):
    type: str
    coordinates: Any


class PlotBase(BaseModel):
    tenant_id: UUID
    farm_id: UUID
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    crop_type: Optional[str] = None
    area_ha: Optional[float] = None


class PlotCreate(PlotBase):
    geom_geojson: GeometryGeoJSON


class PlotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    crop_type: Optional[str] = None
    area_ha: Optional[float] = None
    geom_geojson: Optional[GeometryGeoJSON] = None


class PlotOut(PlotBase):
    id: UUID
    geom_geojson: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
