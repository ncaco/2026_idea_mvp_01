from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List


class TransactionBase(BaseModel):
    category_id: int
    type: str  # 'income' or 'expense'
    amount: Decimal
    description: Optional[str] = None
    transaction_date: date


class TransactionCreate(TransactionBase):
    # user_id는 서버에서 자동 설정되므로 클라이언트에서 보낼 필요 없음
    tag_ids: Optional[List[int]] = None


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    type: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    transaction_date: Optional[date] = None
    tag_ids: Optional[List[int]] = None


class Transaction(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_with_tags(cls, obj):
        """태그 정보를 포함하여 Transaction 객체 생성"""
        data = {
            'id': obj.id,
            'user_id': obj.user_id,
            'category_id': obj.category_id,
            'type': obj.type,
            'amount': obj.amount,
            'description': obj.description,
            'transaction_date': obj.transaction_date,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'tags': [{'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in obj.tags] if hasattr(obj, 'tags') and obj.tags else []
        }
        return cls(**data)
