from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class TransactionTemplateBase(BaseModel):
    name: str
    category_id: int
    type: str  # 'income' or 'expense'
    amount: Decimal
    description: Optional[str] = None


class TransactionTemplateCreate(TransactionTemplateBase):
    pass


class TransactionTemplateUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None


class TransactionTemplate(TransactionTemplateBase):
    id: int
    user_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
