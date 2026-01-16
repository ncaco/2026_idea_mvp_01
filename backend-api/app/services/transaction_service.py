from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date
from app.models import Transaction, Category
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services.elasticsearch_service import (
    index_transaction,
    update_transaction_index,
    delete_transaction_index
)
import logging

logger = logging.getLogger(__name__)


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


def create_transaction(db: Session, transaction: TransactionCreate, user_id: int) -> Transaction:
    """거래 내역 생성"""
    transaction_data = transaction.model_dump()
    transaction_data['user_id'] = user_id
    db_transaction = Transaction(**transaction_data)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    # 엘라스틱서치 인덱싱 (비동기적으로 처리, 실패해도 DB 트랜잭션은 유지)
    try:
        category = db.query(Category).filter(Category.id == db_transaction.category_id).first()
        index_transaction(db, db_transaction, category)
    except Exception as e:
        logger.error(f"엘라스틱서치 인덱싱 실패 (transaction_id={db_transaction.id}): {e}")
        # 인덱싱 실패해도 DB 트랜잭션은 성공으로 처리
    
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
    
    # 엘라스틱서치 인덱스 업데이트
    try:
        category = db.query(Category).filter(Category.id == db_transaction.category_id).first()
        update_transaction_index(db, db_transaction, category)
    except Exception as e:
        logger.error(f"엘라스틱서치 인덱스 업데이트 실패 (transaction_id={transaction_id}): {e}")
    
    return db_transaction


def delete_transaction(db: Session, transaction_id: int, user_id: int) -> bool:
    """거래 내역 삭제"""
    db_transaction = get_transaction(db, transaction_id, user_id)
    if not db_transaction:
        return False
    
    db.delete(db_transaction)
    db.commit()
    
    # 엘라스틱서치 인덱스에서 삭제
    try:
        delete_transaction_index(transaction_id)
    except Exception as e:
        logger.error(f"엘라스틱서치 인덱스 삭제 실패 (transaction_id={transaction_id}): {e}")
    
    return True
