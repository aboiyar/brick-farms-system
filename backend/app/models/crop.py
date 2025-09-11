from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Enum, JSON, text
from app.db.base import Base

class Crop(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    category: Mapped[str] = mapped_column(Enum("crop","tree", name="crop_category"), index=True, nullable=False)
    common_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    scientific_name: Mapped[str] = mapped_column(String(200))
    descriptors: Mapped[dict] = mapped_column(JSON, default=dict)  # required flags & units

class Variety(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    crop_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
