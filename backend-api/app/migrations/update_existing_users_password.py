"""
기존 사용자들의 비밀번호를 'default'로 업데이트
"""
import sqlite3
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)

# 데이터베이스 파일 경로
DB_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DB_DIR, "accountbook.db")


def update_passwords():
    """기존 사용자들의 비밀번호 업데이트"""
    if not os.path.exists(DB_PATH):
        print(f"데이터베이스 파일이 없습니다: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # hashed_password 컬럼이 있는지 확인
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'hashed_password' not in columns:
            print("hashed_password 컬럼이 없습니다. 먼저 마이그레이션을 실행하세요.")
            return
        
        # 비밀번호 해싱
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        default_password_hash = pwd_context.hash("default")
        
        # 기존 사용자들의 비밀번호 업데이트 (비어있거나 NULL인 경우)
        cursor.execute("SELECT id, username, hashed_password FROM users")
        users = cursor.fetchall()
        
        updated_count = 0
        for user_id, username, current_hash in users:
            if not current_hash or current_hash == '':
                cursor.execute(
                    "UPDATE users SET hashed_password = ? WHERE id = ?",
                    (default_password_hash, user_id)
                )
                updated_count += 1
                print(f"사용자 '{username}' (ID: {user_id})의 비밀번호를 업데이트했습니다.")
        
        conn.commit()
        print(f"\n총 {updated_count}명의 사용자 비밀번호가 업데이트되었습니다.")
        
    except Exception as e:
        conn.rollback()
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    update_passwords()
