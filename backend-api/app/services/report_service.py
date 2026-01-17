"""
리포트 생성 서비스
"""
from typing import Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Transaction, Category


def generate_monthly_report(
    db: Session,
    user_id: int,
    year: int,
    month: int
) -> Dict[str, Any]:
    """
    월별 리포트 생성
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        year: 연도
        month: 월
    
    Returns:
        리포트 데이터
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
    
    income = 0
    expense = 0
    income_count = 0
    expense_count = 0
    
    for stat in monthly_stats:
        if stat.type == 'income':
            income = float(stat.total) if stat.total else 0
            income_count = stat.count
        elif stat.type == 'expense':
            expense = float(stat.total) if stat.total else 0
            expense_count = stat.count
    
    balance = income - expense
    
    # 카테고리별 상세 내역
    category_details = db.query(
        Category.id,
        Category.name,
        Category.color,
        Transaction.type,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    ).join(
        Transaction, Category.id == Transaction.category_id
    ).filter(
        Transaction.user_id == user_id,
        extract('year', Transaction.transaction_date) == year,
        extract('month', Transaction.transaction_date) == month
    ).group_by(
        Category.id, Category.name, Category.color, Transaction.type
    ).all()
    
    category_breakdown = []
    for detail in category_details:
        category_breakdown.append({
            'category_id': detail.id,
            'category_name': detail.name,
            'color': detail.color,
            'type': detail.type,
            'total': float(detail.total) if detail.total else 0,
            'count': detail.count
        })
    
    # 거래 내역 목록
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        extract('year', Transaction.transaction_date) == year,
        extract('month', Transaction.transaction_date) == month
    ).order_by(Transaction.transaction_date.desc()).all()
    
    transaction_list = []
    categories_dict = {}
    
    # 카테고리 정보 가져오기
    category_ids = {t.category_id for t in transactions}
    if category_ids:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        categories_dict = {c.id: c for c in categories}
    
    for t in transactions:
        category = categories_dict.get(t.category_id)
        transaction_list.append({
            'id': t.id,
            'date': t.transaction_date.isoformat(),
            'type': t.type,
            'amount': float(t.amount),
            'description': t.description,
            'category_id': t.category_id,
            'category_name': category.name if category else '알 수 없음'
        })
    
    return {
        'year': year,
        'month': month,
        'summary': {
            'income': income,
            'expense': expense,
            'balance': balance,
            'income_count': income_count,
            'expense_count': expense_count
        },
        'category_breakdown': category_breakdown,
        'transactions': transaction_list,
        'generated_at': datetime.now().isoformat()
    }
