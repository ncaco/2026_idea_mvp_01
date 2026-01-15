from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date
from app.models import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


def get_transaction(db: Session, transaction_id: int, user_id: int) -> Optional[Transaction]:
    """거래 내역 조회"""
    return db.query(Transaction).filter(
        and_(Transaction.id == transaction_id, Transaction.user_id == user_id)
    ).first()


def get_transactions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    transaction_type: Optional[str] = None
) -> List[Transaction]:
    """거래 내역 목록 조회 (필터링, 페이지네이션)"""
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    
    return query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()


def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
    """거래 내역 생성"""
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def update_transaction(
    db: Session,
    transaction_id: int,
    user_id: int,
    transaction_update: TransactionUpdate
) -> Optional[Transaction]:
    """거래 내역 수정"""
    db_transaction = get_transaction(db, transaction_id, user_id)
    if not db_transaction:
        return None
    
    update_data = transaction_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, transaction_id: int, user_id: int) -> bool:
    """거래 내역 삭제"""
    db_transaction = get_transaction(db, transaction_id, user_id)
    if not db_transaction:
        return False
    
    db.delete(db_transaction)
    db.commit()
    return True
