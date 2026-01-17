from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_
from typing import List, Optional
from datetime import date
from app.models import Transaction, Category
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
    transaction_type: Optional[str] = None,
    search: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> List[Transaction]:
    """거래 내역 목록 조회 (필터링, 페이지네이션, 검색)"""
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    
    # 금액 범위 검색
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    
    # 검색어가 있는 경우 (설명 또는 카테고리명 검색)
    if search:
        search_term = f"%{search}%"
        # 설명 검색
        description_filter = Transaction.description.ilike(search_term)
        
        # 카테고리명 검색을 위한 서브쿼리
        category_subquery = db.query(Category.id).filter(
            and_(
                Category.user_id == user_id,
                Category.name.ilike(search_term)
            )
        ).subquery()
        category_filter = Transaction.category_id.in_(category_subquery)
        
        # 설명 또는 카테고리명에 검색어가 포함된 경우
        query = query.filter(or_(description_filter, category_filter))
    
    return query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()


def create_transaction(db: Session, transaction: TransactionCreate, user_id: int) -> Transaction:
    """거래 내역 생성"""
    transaction_data = transaction.model_dump()
    transaction_data['user_id'] = user_id
    db_transaction = Transaction(**transaction_data)
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


def delete_all_transactions(
    db: Session,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    transaction_type: Optional[str] = None
) -> int:
    """거래 내역 전체 삭제 (필터 조건 적용 가능)"""
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    
    count = query.count()
    query.delete(synchronize_session=False)
    db.commit()
    return count
