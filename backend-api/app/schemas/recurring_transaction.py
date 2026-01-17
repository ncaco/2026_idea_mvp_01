from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal


class RecurringTransactionBase(BaseModel):
    category_id: int
    type: str = Field(..., pattern="^(income|expense)$")
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    frequency: str = Field(..., pattern="^(daily|weekly|monthly|yearly)$")
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)  # 0=월요일, 6=일요일
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True


class RecurringTransactionCreate(RecurringTransactionBase):
    pass


class RecurringTransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    type: Optional[str] = Field(None, pattern="^(income|expense)$")
    amount: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = None
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|yearly)$")
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class RecurringTransaction(RecurringTransactionBase):
    id: int
    user_id: int
    last_generated_date: Optional[date] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
