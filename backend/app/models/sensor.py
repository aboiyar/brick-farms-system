from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, TIMESTAMP, BigInteger, Double, text, DateTime
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.db.base import Base


class SensorDevice(Base):
    __tablename__ = "sensor_devices"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    farm_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    plot_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    protocol: Mapped[str] = mapped_column(String(20))  # mqtt|coap|http
    api_key: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    device_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    metric: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[float] = mapped_column(Double, nullable=False)
    unit: Mapped[str] = mapped_column(String(24))
    timestamp: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), index=True, nullable=False)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326))
