from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int, user_id: int) -> Optional[Category]:
    """카테고리 조회"""
    return db.query(Category).filter(
        and_(Category.id == category_id, Category.user_id == user_id)
    ).first()


def get_categories(
    db: Session,
    user_id: int,
    category_type: Optional[str] = None
) -> List[Category]:
    """카테고리 목록 조회"""
    query = db.query(Category).filter(Category.user_id == user_id)
    
    if category_type:
        query = query.filter(Category.type == category_type)
    
    return query.order_by(Category.type, Category.name).all()


def create_category(db: Session, category: CategoryCreate, user_id: int) -> Category:
    """카테고리 생성"""
    category_data = category.model_dump()
    category_data['user_id'] = user_id
    db_category = Category(**category_data)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(
    db: Session,
    category_id: int,
    user_id: int,
    category_update: CategoryUpdate
) -> Optional[Category]:
    """카테고리 수정"""
    db_category = get_category(db, category_id, user_id)
    if not db_category:
        return None
    
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int, user_id: int) -> bool:
    """카테고리 삭제"""
    db_category = get_category(db, category_id, user_id)
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True


def delete_all_categories(
    db: Session,
    user_id: int,
    category_type: Optional[str] = None
) -> int:
    """카테고리 전체 삭제 (타입별 필터 적용 가능)"""
    query = db.query(Category).filter(Category.user_id == user_id)
    
    if category_type:
        query = query.filter(Category.type == category_type)
    
    count = query.count()
    query.delete(synchronize_session=False)
    db.commit()
    return count
