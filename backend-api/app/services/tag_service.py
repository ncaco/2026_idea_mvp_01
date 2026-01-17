from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional

from app.models import Tag, Transaction, transaction_tag_association
from app.schemas.tag import TagCreate, TagUpdate


def get_tag(db: Session, tag_id: int, user_id: int) -> Optional[Tag]:
    """태그 조회"""
    return db.query(Tag).filter(
        and_(
            Tag.id == tag_id,
            Tag.user_id == user_id
        )
    ).first()


def get_tags(db: Session, user_id: int) -> List[Tag]:
    """태그 목록 조회"""
    return db.query(Tag).filter(Tag.user_id == user_id).order_by(Tag.name).all()


def get_tags_with_count(db: Session, user_id: int) -> List[dict]:
    """태그 목록 조회 (거래 수 포함)"""
    from sqlalchemy import select
    
    # 명시적으로 FROM 절 지정
    tags = db.query(
        Tag,
        func.count(Transaction.id).label('transaction_count')
    ).select_from(
        Tag
    ).outerjoin(
        transaction_tag_association, Tag.id == transaction_tag_association.c.tag_id
    ).outerjoin(
        Transaction, Transaction.id == transaction_tag_association.c.transaction_id
    ).filter(
        Tag.user_id == user_id
    ).group_by(Tag.id).order_by(Tag.name).all()
    
    result = []
    for tag, count in tags:
        tag_dict = {
            'id': tag.id,
            'user_id': tag.user_id,
            'name': tag.name,
            'color': tag.color,
            'created_at': tag.created_at.isoformat() if tag.created_at else '',
            'updated_at': tag.updated_at.isoformat() if tag.updated_at else '',
            'transaction_count': count or 0,
        }
        result.append(tag_dict)
    
    return result


def create_tag(db: Session, user_id: int, tag_data: TagCreate) -> Tag:
    """태그 생성"""
    # 같은 이름의 태그가 이미 있는지 확인
    existing = db.query(Tag).filter(
        and_(
            Tag.user_id == user_id,
            Tag.name == tag_data.name
        )
    ).first()
    
    if existing:
        raise ValueError(f"태그 '{tag_data.name}'가 이미 존재합니다.")
    
    tag = Tag(
        user_id=user_id,
        **tag_data.model_dump()
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def update_tag(db: Session, tag_id: int, user_id: int, tag_data: TagUpdate) -> Optional[Tag]:
    """태그 수정"""
    tag = get_tag(db, tag_id, user_id)
    if not tag:
        return None
    
    # 이름 변경 시 중복 체크
    if tag_data.name and tag_data.name != tag.name:
        existing = db.query(Tag).filter(
            and_(
                Tag.user_id == user_id,
                Tag.name == tag_data.name,
                Tag.id != tag_id
            )
        ).first()
        if existing:
            raise ValueError(f"태그 '{tag_data.name}'가 이미 존재합니다.")
    
    update_data = tag_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)
    
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag_id: int, user_id: int) -> bool:
    """태그 삭제 (거래와의 연결도 자동으로 삭제됨)"""
    tag = get_tag(db, tag_id, user_id)
    if not tag:
        return False
    
    db.delete(tag)
    db.commit()
    return True


def add_tags_to_transaction(db: Session, transaction_id: int, tag_ids: List[int], user_id: int) -> bool:
    """거래에 태그 추가"""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
    ).first()
    
    if not transaction:
        return False
    
    # 태그들이 해당 사용자의 태그인지 확인
    tags = db.query(Tag).filter(
        and_(
            Tag.id.in_(tag_ids),
            Tag.user_id == user_id
        )
    ).all()
    
    if len(tags) != len(tag_ids):
        return False
    
    # 기존 태그 제거 후 새 태그 추가
    transaction.tags = tags
    db.commit()
    return True


def get_transactions_by_tag(db: Session, tag_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[Transaction]:
    """태그로 거래 조회"""
    return db.query(Transaction).join(
        transaction_tag_association
    ).filter(
        and_(
            Transaction.user_id == user_id,
            transaction_tag_association.c.tag_id == tag_id
        )
    ).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
