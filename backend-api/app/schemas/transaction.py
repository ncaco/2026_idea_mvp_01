from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal
from typing import Optional


class TransactionBase(BaseModel):
    category_id: int
    type: str  # 'income' or 'expense'
    amount: Decimal
    description: Optional[str] = None
    transaction_date: date


class TransactionCreate(TransactionBase):
    user_id: int


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    transaction_date: Optional[date] = None


class Transaction(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
