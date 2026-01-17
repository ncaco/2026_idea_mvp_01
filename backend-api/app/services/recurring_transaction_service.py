from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date, datetime, timedelta
from calendar import monthrange

from app.models import RecurringTransaction, Transaction, Category
from app.schemas.recurring_transaction import RecurringTransactionCreate, RecurringTransactionUpdate


def get_recurring_transaction(db: Session, recurring_id: int, user_id: int) -> Optional[RecurringTransaction]:
    """반복 거래 조회"""
    return db.query(RecurringTransaction).filter(
        and_(
            RecurringTransaction.id == recurring_id,
            RecurringTransaction.user_id == user_id
        )
    ).first()


def get_recurring_transactions(
    db: Session,
    user_id: int,
    is_active: Optional[bool] = None
) -> List[RecurringTransaction]:
    """반복 거래 목록 조회"""
    query = db.query(RecurringTransaction).filter(
        RecurringTransaction.user_id == user_id
    )
    
    if is_active is not None:
        query = query.filter(RecurringTransaction.is_active == is_active)
    
    return query.order_by(RecurringTransaction.created_at.desc()).all()


def create_recurring_transaction(
    db: Session,
    user_id: int,
    recurring_data: RecurringTransactionCreate
) -> RecurringTransaction:
    """반복 거래 생성"""
    recurring = RecurringTransaction(
        user_id=user_id,
        **recurring_data.model_dump()
    )
    db.add(recurring)
    db.commit()
    db.refresh(recurring)
    return recurring


def update_recurring_transaction(
    db: Session,
    recurring_id: int,
    user_id: int,
    recurring_data: RecurringTransactionUpdate
) -> Optional[RecurringTransaction]:
    """반복 거래 수정"""
    recurring = get_recurring_transaction(db, recurring_id, user_id)
    if not recurring:
        return None
    
    update_data = recurring_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recurring, field, value)
    
    db.commit()
    db.refresh(recurring)
    return recurring


def delete_recurring_transaction(db: Session, recurring_id: int, user_id: int) -> bool:
    """반복 거래 삭제"""
    recurring = get_recurring_transaction(db, recurring_id, user_id)
    if not recurring:
        return False
    
    db.delete(recurring)
    db.commit()
    return True


def generate_transactions_from_recurring(
    db: Session,
    user_id: int,
    target_date: Optional[date] = None,
    generate_past: bool = False
) -> List[Transaction]:
    """반복 거래에서 실제 거래 생성
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        target_date: 거래 생성 대상 날짜 (기본값: 오늘)
        generate_past: 과거 날짜도 생성할지 여부 (기본값: False, 오늘만 생성)
    """
    if target_date is None:
        target_date = date.today()
    
    # 활성화된 반복 거래 조회
    recurring_list = get_recurring_transactions(db, user_id, is_active=True)
    
    generated_transactions = []
    
    for recurring in recurring_list:
        # 종료일 체크
        if recurring.end_date and target_date > recurring.end_date:
            continue
        
        # 시작일 체크 (시작일 당일부터 생성 가능)
        if target_date < recurring.start_date:
            continue
        
        # 과거 날짜 생성 옵션이 없으면 오늘만 체크
        if not generate_past and target_date < date.today():
            continue
        
        # 이미 생성된 거래인지 확인 (같은 날짜에 이미 생성된 경우 스킵)
        if recurring.last_generated_date and target_date <= recurring.last_generated_date:
            # 같은 날짜면 스킵, 과거 날짜도 스킵
            continue
        
        # 반복 주기에 따라 거래 생성 여부 결정
        should_generate = False
        
        if recurring.frequency == 'daily':
            should_generate = True
        
        elif recurring.frequency == 'weekly':
            if recurring.day_of_week is not None:
                # Python의 weekday(): 0=월요일, 6=일요일
                weekday = target_date.weekday()  # 0=월요일, 6=일요일
                should_generate = (weekday == recurring.day_of_week)
            else:
                # 요일이 지정되지 않으면 시작일의 요일과 같은 요일
                start_weekday = recurring.start_date.weekday()
                should_generate = (target_date.weekday() == start_weekday)
        
        elif recurring.frequency == 'monthly':
            if recurring.day_of_month is not None:
                # 매월 지정된 날짜
                # 해당 월의 마지막 날이 지정일보다 작으면 마지막 날에 생성
                last_day = monthrange(target_date.year, target_date.month)[1]
                if recurring.day_of_month > last_day:
                    should_generate = (target_date.day == last_day)
                else:
                    should_generate = (target_date.day == recurring.day_of_month)
            else:
                # 매월 마지막 날
                last_day = monthrange(target_date.year, target_date.month)[1]
                should_generate = (target_date.day == last_day)
        
        elif recurring.frequency == 'yearly':
            # 매년 같은 월/일
            should_generate = (
                target_date.month == recurring.start_date.month and
                target_date.day == recurring.start_date.day
            )
        
        if should_generate:
            # 거래 생성
            transaction = Transaction(
                user_id=user_id,
                category_id=recurring.category_id,
                type=recurring.type,
                amount=recurring.amount,
                description=recurring.description or f"[반복 거래]",
                transaction_date=target_date
            )
            db.add(transaction)
            generated_transactions.append(transaction)
            
            # 마지막 생성일 업데이트 (더 최근 날짜로)
            if not recurring.last_generated_date or target_date > recurring.last_generated_date:
                recurring.last_generated_date = target_date
    
    if generated_transactions:
        db.commit()
        for transaction in generated_transactions:
            db.refresh(transaction)
    
    return generated_transactions
