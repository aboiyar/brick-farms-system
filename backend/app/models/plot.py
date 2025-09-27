from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Float, Text
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from geoalchemy2 import Geometry
from app.db.base import Base
from sqlalchemy import text


class Plot(Base):
    __tablename__ = "plots"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    farm_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    crop_type: Mapped[str] = mapped_column(String(120))
    area_ha: Mapped[float] = mapped_column(Float)
    geom = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
