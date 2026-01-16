from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.services import category_service
from app.core.security import get_current_user
from app.models import User

router = APIRouter()


@router.get("", response_model=List[Category])
def get_categories(
    type: Optional[str] = Query(None, regex="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 목록 조회"""
    return category_service.get_categories(
        db=db,
        user_id=current_user.id,
        category_type=type
    )


@router.post("", response_model=Category, status_code=201)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 생성"""
    return category_service.create_category(db, category, current_user.id)


@router.get("/{category_id}", response_model=Category)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 상세 조회"""
    category = category_service.get_category(db, category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return category


@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 수정"""
    category = category_service.update_category(
        db, category_id, current_user.id, category_update
    )
    if not category:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """카테고리 삭제"""
    success = category_service.delete_category(db, category_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다")
    return None
