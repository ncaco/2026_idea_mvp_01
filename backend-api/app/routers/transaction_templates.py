from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.transaction_template import (
    TransactionTemplate,
    TransactionTemplateCreate,
    TransactionTemplateUpdate
)
from app.services import transaction_template_service

router = APIRouter()


@router.get("", response_model=List[TransactionTemplate])
def get_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """템플릿 목록 조회"""
    return transaction_template_service.get_templates(db, current_user.id)


@router.get("/{template_id}", response_model=TransactionTemplate)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """템플릿 상세 조회"""
    template = transaction_template_service.get_template(db, template_id, current_user.id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="템플릿을 찾을 수 없습니다."
        )
    return template


@router.post("", response_model=TransactionTemplate, status_code=status.HTTP_201_CREATED)
def create_template(
    template_data: TransactionTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """템플릿 생성"""
    return transaction_template_service.create_template(
        db, current_user.id, template_data
    )


@router.put("/{template_id}", response_model=TransactionTemplate)
def update_template(
    template_id: int,
    template_data: TransactionTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """템플릿 수정"""
    template = transaction_template_service.update_template(
        db, template_id, current_user.id, template_data
    )
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="템플릿을 찾을 수 없습니다."
        )
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """템플릿 삭제"""
    success = transaction_template_service.delete_template(
        db, template_id, current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="템플릿을 찾을 수 없습니다."
        )
