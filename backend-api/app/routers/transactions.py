from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.schemas.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.services import transaction_service

router = APIRouter()

# Phase 1에서는 기본 사용자 ID 1 사용
DEFAULT_USER_ID = 1


@router.post("", response_model=Transaction, status_code=201)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """거래 내역 생성"""
    transaction.user_id = DEFAULT_USER_ID
    return transaction_service.create_transaction(db, transaction)


@router.get("", response_model=List[Transaction])
def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None, regex="^(income|expense)$"),
    db: Session = Depends(get_db)
):
    """거래 내역 목록 조회"""
    return transaction_service.get_transactions(
        db=db,
        user_id=DEFAULT_USER_ID,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        transaction_type=type
    )


@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """거래 내역 상세 조회"""
    transaction = transaction_service.get_transaction(db, transaction_id, DEFAULT_USER_ID)
    if not transaction:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    return transaction


@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """거래 내역 수정"""
    transaction = transaction_service.update_transaction(
        db, transaction_id, DEFAULT_USER_ID, transaction_update
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    return transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """거래 내역 삭제"""
    success = transaction_service.delete_transaction(db, transaction_id, DEFAULT_USER_ID)
    if not success:
        raise HTTPException(status_code=404, detail="거래 내역을 찾을 수 없습니다")
    return None
