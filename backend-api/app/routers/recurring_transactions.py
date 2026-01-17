from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.recurring_transaction import (
    RecurringTransaction,
    RecurringTransactionCreate,
    RecurringTransactionUpdate
)
from app.services import recurring_transaction_service

router = APIRouter()


@router.get("", response_model=List[RecurringTransaction])
def get_recurring_transactions(
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반복 거래 목록 조회"""
    return recurring_transaction_service.get_recurring_transactions(
        db, current_user.id, is_active
    )


@router.get("/{recurring_id}", response_model=RecurringTransaction)
def get_recurring_transaction(
    recurring_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반복 거래 상세 조회"""
    recurring = recurring_transaction_service.get_recurring_transaction(
        db, recurring_id, current_user.id
    )
    if not recurring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="반복 거래를 찾을 수 없습니다."
        )
    return recurring


@router.post("", response_model=RecurringTransaction, status_code=status.HTTP_201_CREATED)
def create_recurring_transaction(
    recurring_data: RecurringTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반복 거래 생성"""
    return recurring_transaction_service.create_recurring_transaction(
        db, current_user.id, recurring_data
    )


@router.put("/{recurring_id}", response_model=RecurringTransaction)
def update_recurring_transaction(
    recurring_id: int,
    recurring_data: RecurringTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반복 거래 수정"""
    recurring = recurring_transaction_service.update_recurring_transaction(
        db, recurring_id, current_user.id, recurring_data
    )
    if not recurring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="반복 거래를 찾을 수 없습니다."
        )
    return recurring


@router.delete("/{recurring_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring_transaction(
    recurring_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반복 거래 삭제"""
    success = recurring_transaction_service.delete_recurring_transaction(
        db, recurring_id, current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="반복 거래를 찾을 수 없습니다."
        )


@router.post("/generate", status_code=status.HTTP_200_OK)
def generate_transactions(
    target_date: Optional[date] = Query(None, description="거래 생성 대상 날짜 (기본값: 오늘)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """반복 거래에서 실제 거래 생성"""
    transactions = recurring_transaction_service.generate_transactions_from_recurring(
        db, current_user.id, target_date
    )
    return {
        "message": f"{len(transactions)}개의 거래가 생성되었습니다.",
        "count": len(transactions),
        "transactions": transactions
    }
