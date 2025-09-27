from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class DeviceIn(BaseModel):
    farm_id: UUID
    plot_id: Optional[UUID] = None
    name: str = Field(..., max_length=120)
    protocol: str = "http"
    api_key: str


class DeviceOut(DeviceIn):
    id: UUID

    class Config:
        from_attributes = True


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    protocol: Optional[str] = None
    plot_id: Optional[UUID] = None
    api_key: Optional[str] = None


class ReadingIn(BaseModel):
    device_id: UUID
    metric: str
    value: float
    unit: Optional[str] = None
    timestamp: Optional[datetime] = None
    location: Optional[Dict[str, Any]] = None  # GeoJSON point


class ReadingOut(ReadingIn):
    id: int

    class Config:
        from_attributes = True
