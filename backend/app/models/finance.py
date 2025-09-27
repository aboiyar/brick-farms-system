from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa
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


class FinanceTransaction(Base):
    __tablename__ = 'finance_transactions'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    account_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14,2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="NGN")
    ts: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    description: Mapped[str] = mapped_column(String(400))
    meta: Mapped[dict] = mapped_column(JSON, default=dict)


class Investment(Base):
    __tablename__ = 'investments'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14,2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="NGN")
    ts: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)


class Payout(Base):
    __tablename__ = 'payouts'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    investment_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14,2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="NGN")
    ts: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    note: Mapped[str] = mapped_column(String(400))


class Receipt(Base):
    __tablename__ = 'receipts'
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    investment_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255))
    content: Mapped[bytes] = mapped_column(sa.LargeBinary)
