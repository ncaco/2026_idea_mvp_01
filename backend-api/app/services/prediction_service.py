"""
지출 예측 서비스
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Transaction, Category


def predict_next_month_expense(
    db: Session,
    user_id: int,
    months_back: int = 6
) -> Dict[str, Any]:
    """
    다음 달 지출 예측 (간단한 선형 회귀 기반)
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        months_back: 예측에 사용할 과거 개월 수
    
    Returns:
        예측 결과
    """
    # 과거 N개월 데이터 수집
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=months_back * 30)
    
    monthly_expenses = db.query(
        extract('year', Transaction.transaction_date).label('year'),
        extract('month', Transaction.transaction_date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).group_by(
        extract('year', Transaction.transaction_date),
        extract('month', Transaction.transaction_date)
    ).order_by(
        extract('year', Transaction.transaction_date),
        extract('month', Transaction.transaction_date)
    ).all()
    
    if len(monthly_expenses) < 2:
        # 데이터가 부족하면 평균 사용
        avg_expense = db.query(func.avg(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense'
        ).scalar() or 0
        
        # 월별 평균 거래 건수 추정
        count = db.query(func.count(Transaction.id)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense'
        ).scalar() or 0
        
        estimated_monthly = float(avg_expense) * max(count / max(months_back, 1), 1)
        
        return {
            'predicted_total': estimated_monthly,
            'predicted_by_category': [],
            'method': 'average',
            'confidence': 0.3
        }
    
    # 간단한 선형 회귀 (최소 제곱법)
    # y = ax + b 형태로 예측
    n = len(monthly_expenses)
    x_values = list(range(n))
    y_values = [float(row.total) if row.total else 0 for row in monthly_expenses]
    
    # 평균 계산
    x_mean = sum(x_values) / n
    y_mean = sum(y_values) / n
    
    # 기울기와 절편 계산
    numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
    denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        # 모든 값이 같으면 평균 사용
        predicted = y_mean
        confidence = 0.5
    else:
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # 다음 달 예측 (x = n)
        predicted = slope * n + intercept
        confidence = min(0.9, max(0.3, 1.0 - abs(slope) / max(y_mean, 1) * 10))
    
    # 카테고리별 예측
    category_predictions = []
    
    category_expenses = db.query(
        Category.id,
        Category.name,
        Category.color,
        extract('year', Transaction.transaction_date).label('year'),
        extract('month', Transaction.transaction_date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).join(
        Transaction, Category.id == Transaction.category_id
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    ).group_by(
        Category.id, Category.name, Category.color,
        extract('year', Transaction.transaction_date),
        extract('month', Transaction.transaction_date)
    ).all()
    
    # 카테고리별로 그룹화
    category_monthly = {}
    for row in category_expenses:
        cat_id = row.id
        if cat_id not in category_monthly:
            category_monthly[cat_id] = {
                'name': row.name,
                'color': row.color,
                'amounts': []
            }
        category_monthly[cat_id]['amounts'].append(float(row.total) if row.total else 0)
    
    # 각 카테고리별 예측
    for cat_id, data in category_monthly.items():
        amounts = data['amounts']
        if len(amounts) >= 2:
            # 선형 회귀
            x_cat = list(range(len(amounts)))
            y_cat = amounts
            x_mean_cat = sum(x_cat) / len(x_cat)
            y_mean_cat = sum(y_cat) / len(y_cat)
            
            num_cat = sum((x_cat[i] - x_mean_cat) * (y_cat[i] - y_mean_cat) for i in range(len(x_cat)))
            den_cat = sum((x_cat[i] - x_mean_cat) ** 2 for i in range(len(x_cat)))
            
            if den_cat != 0:
                slope_cat = num_cat / den_cat
                intercept_cat = y_mean_cat - slope_cat * x_mean_cat
                predicted_cat = slope_cat * len(amounts) + intercept_cat
            else:
                predicted_cat = y_mean_cat
        else:
            predicted_cat = sum(amounts) / len(amounts) if amounts else 0
        
        category_predictions.append({
            'category_id': cat_id,
            'category_name': data['name'],
            'color': data['color'],
            'predicted_amount': max(0, predicted_cat)
        })
    
    return {
        'predicted_total': max(0, predicted),
        'predicted_by_category': category_predictions,
        'method': 'linear_regression',
        'confidence': confidence,
        'based_on_months': len(monthly_expenses)
    }
