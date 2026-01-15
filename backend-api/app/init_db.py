"""
데이터베이스 초기화 및 초기 데이터 삽입 스크립트
"""
from app.database import init_db, SessionLocal
from app.models import User, Category


def create_default_user(db):
    """기본 사용자 생성"""
    user = db.query(User).filter(User.username == "default").first()
    if not user:
        user = User(username="default", email="user@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"기본 사용자 생성 완료: {user.username} (ID: {user.id})")
    return user


def create_default_categories(db, user_id: int):
    """기본 카테고리 생성"""
    default_categories = [
        # 수입 카테고리
        {"name": "급여", "type": "income", "color": "#4CAF50"},
        {"name": "용돈", "type": "income", "color": "#8BC34A"},
        {"name": "기타 수입", "type": "income", "color": "#CDDC39"},
        # 지출 카테고리
        {"name": "식비", "type": "expense", "color": "#F44336"},
        {"name": "교통비", "type": "expense", "color": "#FF9800"},
        {"name": "쇼핑", "type": "expense", "color": "#9C27B0"},
        {"name": "의료비", "type": "expense", "color": "#2196F3"},
        {"name": "교육비", "type": "expense", "color": "#00BCD4"},
        {"name": "기타 지출", "type": "expense", "color": "#607D8B"},
    ]

    created_count = 0
    for cat_data in default_categories:
        existing = db.query(Category).filter(
            Category.name == cat_data["name"],
            Category.user_id == user_id,
            Category.type == cat_data["type"]
        ).first()
        
        if not existing:
            category = Category(
                name=cat_data["name"],
                type=cat_data["type"],
                color=cat_data["color"],
                user_id=user_id
            )
            db.add(category)
            created_count += 1

    if created_count > 0:
        db.commit()
        print(f"기본 카테고리 {created_count}개 생성 완료")
    else:
        print("모든 기본 카테고리가 이미 존재합니다.")


def main():
    """데이터베이스 초기화 및 초기 데이터 삽입"""
    print("데이터베이스 초기화 시작...")
    
    # 테이블 생성
    init_db()
    print("테이블 생성 완료")
    
    # 초기 데이터 삽입
    db = SessionLocal()
    try:
        user = create_default_user(db)
        create_default_categories(db, user.id)
        print("데이터베이스 초기화 완료!")
        print(f"기본 사용자 ID: {user.id}")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
