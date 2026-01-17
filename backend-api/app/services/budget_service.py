from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from app.models import Budget, Transaction, Category
from app.schemas.budget import BudgetCreate, BudgetUpdate


def get_budget(db: Session, budget_id: int, user_id: int) -> Optional[Budget]:
    """예산 조회"""
    return db.query(Budget).filter(
        and_(Budget.id == budget_id, Budget.user_id == user_id)
    ).first()


def get_budgets(
    db: Session,
    user_id: int,
    month: Optional[str] = None,
    category_id: Optional[int] = None
) -> List[Budget]:
    """예산 목록 조회"""
    query = db.query(Budget).filter(Budget.user_id == user_id)
    
    if month:
        query = query.filter(Budget.month == month)
    if category_id is not None:
        query = query.filter(Budget.category_id == category_id)
    
    return query.order_by(Budget.month.desc(), Budget.category_id).all()


def create_budget(db: Session, budget: BudgetCreate, user_id: int) -> Budget:
    """예산 생성"""
    budget_data = budget.model_dump()
    budget_data['user_id'] = user_id
    db_budget = Budget(**budget_data)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


def update_budget(
    db: Session,
    budget_id: int,
    user_id: int,
    budget_update: BudgetUpdate
) -> Optional[Budget]:
    """예산 수정"""
    db_budget = get_budget(db, budget_id, user_id)
    if not db_budget:
        return None
    
    update_data = budget_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_budget, field, value)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget


def delete_budget(db: Session, budget_id: int, user_id: int) -> bool:
    """예산 삭제"""
    db_budget = get_budget(db, budget_id, user_id)
    if not db_budget:
        return False
    
    db.delete(db_budget)
    db.commit()
    return True


def get_budget_status(
    db: Session,
    user_id: int,
    month: str
) -> List[dict]:
    """예산 대비 지출 현황 조회"""
    # 해당 월의 예산 조회
    budgets = get_budgets(db, user_id, month=month)
    
    # 해당 월의 지출 내역 조회
    year, month_num = map(int, month.split('-'))
    
    expenses = db.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label('total')
    ).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            extract('year', Transaction.transaction_date) == year,
            extract('month', Transaction.transaction_date) == month_num
        )
    ).group_by(Transaction.category_id).all()
    
    expenses_dict = {exp.category_id: float(exp.total) for exp in expenses}
    
    # 전체 지출 합계
    total_expenses = sum(expenses_dict.values())
    
    # 예산별 현황 계산
    status_list = []
    
    for budget in budgets:
        if budget.category_id:
            # 카테고리별 예산
            spent = expenses_dict.get(budget.category_id, 0.0)
            category = db.query(Category).filter(Category.id == budget.category_id).first()
            category_name = category.name if category else None
        else:
            # 전체 예산
            spent = total_expenses
            category_name = None
        
        budget_amount = float(budget.amount)
        remaining = budget_amount - spent
        percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
        is_over = spent > budget_amount
        
        status_list.append({
            'budget_id': budget.id,
            'budget_amount': budget_amount,
            'spent_amount': spent,
            'remaining_amount': remaining,
            'percentage': percentage,
            'is_over_budget': is_over,
            'category_id': budget.category_id,
            'category_name': category_name,
            'month': budget.month
        })
    
    return status_list
