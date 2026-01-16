"""
users 테이블에 hashed_password 컬럼 추가 마이그레이션
"""
import sqlite3
import os

# 데이터베이스 파일 경로 (프로젝트 루트 기준)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # backend-api/app/migrations
APP_DIR = os.path.dirname(SCRIPT_DIR)  # backend-api/app
BACKEND_DIR = os.path.dirname(APP_DIR)  # backend-api
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)  # 프로젝트 루트
DB_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DB_DIR, "accountbook.db")


def migrate():
    """hashed_password 컬럼 추가"""
    if not os.path.exists(DB_PATH):
        print(f"데이터베이스 파일이 없습니다: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # hashed_password 컬럼이 이미 있는지 확인
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'hashed_password' in columns:
            print("hashed_password 컬럼이 이미 존재합니다.")
            return
        
        # hashed_password 컬럼 추가
        print("hashed_password 컬럼 추가 중...")
        cursor.execute("ALTER TABLE users ADD COLUMN hashed_password TEXT NOT NULL DEFAULT ''")
        
        # 기존 사용자들의 비밀번호를 'default'로 설정
        # passlib의 bcrypt를 직접 사용
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        default_password_hash = pwd_context.hash("default")
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE hashed_password = ''",
            (default_password_hash,)
        )
        
        conn.commit()
        print("마이그레이션 완료: hashed_password 컬럼이 추가되었습니다.")
        
    except Exception as e:
        conn.rollback()
        print(f"마이그레이션 오류: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
