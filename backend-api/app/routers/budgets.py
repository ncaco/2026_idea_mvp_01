from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.schemas.budget import Budget, BudgetCreate, BudgetUpdate, BudgetStatus
from app.services import budget_service
from app.core.security import get_current_user
from app.models import User

router = APIRouter()


@router.get("", response_model=List[Budget])
def get_budgets(
    month: Optional[str] = Query(None, description="예산 월 (YYYY-MM 형식)"),
    category_id: Optional[int] = Query(None, description="카테고리 ID (None이면 전체 예산)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예산 목록 조회"""
    return budget_service.get_budgets(
        db=db,
        user_id=current_user.id,
        month=month,
        category_id=category_id
    )


@router.post("", response_model=Budget, status_code=201)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예산 생성"""
    # 월 형식 검증
    try:
        datetime.strptime(budget.month, '%Y-%m')
    except ValueError:
        raise HTTPException(status_code=400, detail="월 형식이 올바르지 않습니다. YYYY-MM 형식을 사용하세요.")
    
    return budget_service.create_budget(db, budget, current_user.id)


@router.get("/{budget_id}", response_model=Budget)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예산 상세 조회"""
    budget = budget_service.get_budget(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=404, detail="예산을 찾을 수 없습니다")
    return budget


@router.put("/{budget_id}", response_model=Budget)
def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예산 수정"""
    if budget_update.month:
        try:
            datetime.strptime(budget_update.month, '%Y-%m')
        except ValueError:
            raise HTTPException(status_code=400, detail="월 형식이 올바르지 않습니다. YYYY-MM 형식을 사용하세요.")
    
    budget = budget_service.update_budget(
        db, budget_id, current_user.id, budget_update
    )
    if not budget:
        raise HTTPException(status_code=404, detail="예산을 찾을 수 없습니다")
    return budget


@router.delete("/{budget_id}", status_code=204)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예산 삭제"""
    success = budget_service.delete_budget(db, budget_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="예산을 찾을 수 없습니다")
    return None


@router.get("/status/{month}", response_model=List[BudgetStatus])
def get_budget_status(
    month: str = Path(..., description="예산 월 (YYYY-MM 형식)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """예산 대비 지출 현황 조회"""
    # 월 형식 검증
    try:
        datetime.strptime(month, '%Y-%m')
    except ValueError:
        raise HTTPException(status_code=400, detail="월 형식이 올바르지 않습니다. YYYY-MM 형식을 사용하세요.")
    
    status_list = budget_service.get_budget_status(db, current_user.id, month)
    return status_list
