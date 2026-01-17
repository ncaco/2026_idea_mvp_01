from pydantic import BaseModel
from typing import Optional


class MonthlyStatistics(BaseModel):
    income: float
    expense: float
    balance: float
    income_count: int
    expense_count: int


class CategoryStatistics(BaseModel):
    category_id: int
    category_name: str
    category_color: Optional[str] = None
    total: float
    count: int
