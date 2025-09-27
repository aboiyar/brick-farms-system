from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID


class TransactionIn(BaseModel):
    account_id: UUID
    amount: float
    currency: Optional[str] = "NGN"
    ts: Optional[datetime] = None
    description: Optional[str] = None
    meta: Optional[Dict] = None


class TransactionOut(TransactionIn):
    id: UUID

    class Config:
        from_attributes = True


class InvestmentIn(BaseModel):
    name: str = Field(..., max_length=200)
    amount: float
    currency: Optional[str] = "NGN"
    ts: Optional[datetime] = None
    meta: Optional[Dict] = None


class InvestmentOut(InvestmentIn):
    id: UUID

    class Config:
        from_attributes = True


class PayoutIn(BaseModel):
    investment_id: UUID
    amount: float
    currency: Optional[str] = "NGN"
    ts: Optional[datetime] = None
    note: Optional[str] = None


class PayoutOut(PayoutIn):
    id: UUID

    class Config:
        from_attributes = True
