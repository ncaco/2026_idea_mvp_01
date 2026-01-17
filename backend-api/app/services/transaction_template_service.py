from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional

from app.models import TransactionTemplate
from app.schemas.transaction_template import TransactionTemplateCreate, TransactionTemplateUpdate


def get_template(db: Session, template_id: int, user_id: int) -> Optional[TransactionTemplate]:
    """템플릿 조회"""
    return db.query(TransactionTemplate).filter(
        and_(
            TransactionTemplate.id == template_id,
            TransactionTemplate.user_id == user_id
        )
    ).first()


def get_templates(db: Session, user_id: int) -> List[TransactionTemplate]:
    """템플릿 목록 조회"""
    return db.query(TransactionTemplate).filter(
        TransactionTemplate.user_id == user_id
    ).order_by(TransactionTemplate.name).all()


def create_template(
    db: Session,
    user_id: int,
    template_data: TransactionTemplateCreate
) -> TransactionTemplate:
    """템플릿 생성"""
    template = TransactionTemplate(
        user_id=user_id,
        **template_data.model_dump()
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def update_template(
    db: Session,
    template_id: int,
    user_id: int,
    template_data: TransactionTemplateUpdate
) -> Optional[TransactionTemplate]:
    """템플릿 수정"""
    template = get_template(db, template_id, user_id)
    if not template:
        return None
    
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template


def delete_template(db: Session, template_id: int, user_id: int) -> bool:
    """템플릿 삭제"""
    template = get_template(db, template_id, user_id)
    if not template:
        return False
    
    db.delete(template)
    db.commit()
    return True
