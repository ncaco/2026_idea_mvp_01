"""
통계 서비스
"""
from typing import Dict, Any, List
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from app.models import Transaction, Category
from app.schemas.statistics import MonthlyStatistics, CategoryStatistics


def get_monthly_statistics(
    db: Session,
    user_id: int,
    year: int,
    month: int
) -> MonthlyStatistics:
    """
    월별 통계 조회
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        year: 연도
        month: 월
    
    Returns:
        월별 통계 데이터
    """
    # 월별 수입/지출 합계
    monthly_stats = db.query(
        Transaction.type,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    ).filter(
        Transaction.user_id == user_id,
        extract('year', Transaction.transaction_date) == year,
        extract('month', Transaction.transaction_date) == month
    ).group_by(Transaction.type).all()
    
    income = Decimal('0')
    expense = Decimal('0')
    income_count = 0
    expense_count = 0
    
    for stat in monthly_stats:
        if stat.type == 'income':
            income = stat.total if stat.total else Decimal('0')
            income_count = stat.count
        elif stat.type == 'expense':
            expense = stat.total if stat.total else Decimal('0')
            expense_count = stat.count
    
    balance = income - expense
    
    return MonthlyStatistics(
        income=float(income),
        expense=float(expense),
        balance=float(balance),
        income_count=income_count,
        expense_count=expense_count
    )


def get_category_statistics(
    db: Session,
    user_id: int,
    year: int,
    month: int,
    transaction_type: str
) -> List[CategoryStatistics]:
    """
    카테고리별 통계 조회
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        year: 연도
        month: 월
        transaction_type: 거래 타입 ('income' or 'expense')
    
    Returns:
        카테고리별 통계 리스트
    """
    # 카테고리별 통계
    category_stats = db.query(
        Category.id,
        Category.name,
        Category.color,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    ).join(
        Transaction, Category.id == Transaction.category_id
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == transaction_type,
        extract('year', Transaction.transaction_date) == year,
        extract('month', Transaction.transaction_date) == month
    ).group_by(
        Category.id, Category.name, Category.color
    ).all()
    
    result = []
    for stat in category_stats:
        result.append(CategoryStatistics(
            category_id=stat.id,
            category_name=stat.name,
            category_color=stat.color,
            total=float(stat.total) if stat.total else 0.0,
            count=stat.count
        ))
    
    return result
