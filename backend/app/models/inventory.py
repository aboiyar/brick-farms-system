from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, JSON, Numeric, text, Enum
from app.db.base import Base

class Item(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True)  # seed/fertilizer/pesticide/tool/...
    descriptors: Mapped[dict] = mapped_column(JSON, default=dict)

class StockTransaction(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    item_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    tx_type: Mapped[str] = mapped_column(Enum("receive","issue","adjust", name="stock_tx_type"), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(12,3), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="kg")
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
