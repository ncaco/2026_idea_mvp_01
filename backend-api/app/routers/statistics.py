from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List, Optional
from datetime import date, datetime
from app.database import get_db
from app.models import Transaction, Category, User
from app.core.security import get_current_user

router = APIRouter()


@router.get("/monthly")
def get_monthly_statistics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """월별 수입/지출 합계"""
    query = db.query(
        Transaction.type,
        func.sum(Transaction.amount).label("total")
    ).filter(Transaction.user_id == current_user.id)
    
    if year:
        query = query.filter(extract("year", Transaction.transaction_date) == year)
    if month:
        query = query.filter(extract("month", Transaction.transaction_date) == month)
    
    results = query.group_by(Transaction.type).all()
    
    income = 0
    expense = 0
    
    for result in results:
        if result.type == "income":
            income = float(result.total) if result.total else 0
        elif result.type == "expense":
            expense = float(result.total) if result.total else 0
    
    return {
        "income": income,
        "expense": expense,
        "balance": income - expense,
        "year": year,
        "month": month
    }


@router.get("/by-category")
def get_category_statistics(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    type: str = Query("expense", regex="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리별 지출/수입 통계"""
    query = db.query(
        Category.id,
        Category.name,
        Category.color,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count")
    ).join(
        Transaction, Category.id == Transaction.category_id
    ).filter(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.type == type
        )
    )
    
    if year:
        query = query.filter(extract("year", Transaction.transaction_date) == year)
    if month:
        query = query.filter(extract("month", Transaction.transaction_date) == month)
    
    results = query.group_by(Category.id, Category.name, Category.color).all()
    
    return [
        {
            "category_id": result.id,
            "category_name": result.name,
            "color": result.color,
            "total": float(result.total) if result.total else 0,
            "count": result.count
        }
        for result in results
    ]


@router.get("/predict-expense")
def predict_expense(
    months_back: int = Query(6, ge=2, le=12, description="예측에 사용할 과거 개월 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """다음 달 지출 예측"""
    from app.services import prediction_service
    
    result = prediction_service.predict_next_month_expense(
        db=db,
        user_id=current_user.id,
        months_back=months_back
    )
    return result
