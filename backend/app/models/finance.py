from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Numeric, JSON, Enum, text, TIMESTAMP
from app.db.base import Base

class Account(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[str] = mapped_column(Enum("asset","liability","equity","income","expense", name="acct_type"), nullable=False)

class LedgerEntry(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    account_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14,2), nullable=False)  # positive=debit/credit depends on type
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    ts: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
