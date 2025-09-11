from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, TIMESTAMP, JSON, text
from app.db.base import Base

class AuditLog(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity: Mapped[str] = mapped_column(String(120))
    entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    ts: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
