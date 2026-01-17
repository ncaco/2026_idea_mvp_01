from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.services import statistics_service, tag_service
from app.schemas.statistics import MonthlyStatistics, CategoryStatistics

router = APIRouter()


@router.get("/monthly", response_model=MonthlyStatistics)
def get_monthly_statistics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """월별 통계 조회"""
    if year is None or month is None:
        now = date.today()
        year = year or now.year
        month = month or now.month
    
    return statistics_service.get_monthly_statistics(db, current_user.id, year, month)


@router.get("/by-category", response_model=list[CategoryStatistics])
def get_category_statistics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    type: str = Query("expense", regex="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리별 통계 조회"""
    if year is None or month is None:
        now = date.today()
        year = year or now.year
        month = month or now.month
    
    return statistics_service.get_category_statistics(db, current_user.id, year, month, type)


@router.get("/by-tag")
def get_tag_statistics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    type: str = Query("expense", regex="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """태그별 통계 조회"""
    if year is None or month is None:
        now = date.today()
        year = year or now.year
        month = month or now.month
    
    # 태그 목록 조회
    tags = tag_service.get_tags_with_count(db, current_user.id)
    
    # 각 태그별 거래 통계 계산
    from datetime import datetime
    from app.models import Transaction, transaction_tag_association
    from sqlalchemy import and_, func, extract
    
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
    
    result = []
    for tag_info in tags:
        tag_id = tag_info['id']
        
        # 해당 태그가 붙은 거래 조회
        transactions = db.query(Transaction).join(
            transaction_tag_association
        ).filter(
            and_(
                Transaction.user_id == current_user.id,
                transaction_tag_association.c.tag_id == tag_id,
                Transaction.type == type,
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date < end_date
            )
        ).all()
        
        total = sum(float(t.amount) for t in transactions)
        count = len(transactions)
        
        if count > 0:  # 거래가 있는 태그만 반환
            result.append({
                'tag_id': tag_id,
                'tag_name': tag_info['name'],
                'tag_color': tag_info.get('color'),
                'total': total,
                'count': count,
            })
    
    return result


@router.get("/predict-expense")
def predict_expense(
    months_back: int = Query(6, ge=2, le=12, description="예측에 사용할 과거 개월 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """다음 달 지출 예측"""
    from app.services import prediction_service
    return prediction_service.predict_next_month_expense(db, current_user.id, months_back)
