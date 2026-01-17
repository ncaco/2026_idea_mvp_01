from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional


class BudgetBase(BaseModel):
    category_id: Optional[int] = None  # None이면 전체 예산
    amount: Decimal
    month: str  # YYYY-MM 형식


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[Decimal] = None
    month: Optional[str] = None


class Budget(BudgetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetStatus(BaseModel):
    """예산 대비 지출 현황"""
    budget_id: int
    budget_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage: float  # 사용률 (0-100)
    is_over_budget: bool
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    month: str
