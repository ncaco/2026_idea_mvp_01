"""
채팅 히스토리 테이블 추가 마이그레이션
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
import os
from pathlib import Path

# 데이터베이스 파일 경로
BASE_DIR = Path(__file__).parent.parent.parent
DB_DIR = BASE_DIR / ".." / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_DIR / 'accountbook.db'}"

def migrate():
    """채팅 히스토리 테이블 생성"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 테이블이 이미 존재하는지 확인
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='chat_history'
        """))
        
        if result.fetchone():
            print("chat_history 테이블이 이미 존재합니다.")
            return
        
        # 테이블 생성
        conn.execute(text("""
            CREATE TABLE chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # 인덱스 생성
        conn.execute(text("""
            CREATE INDEX idx_user_chat_date ON chat_history(user_id, created_at)
        """))
        
        conn.commit()
        print("chat_history 테이블이 생성되었습니다.")

if __name__ == "__main__":
    print("=" * 50)
    print("채팅 히스토리 테이블 마이그레이션")
    print("=" * 50)
    migrate()
    print("마이그레이션 완료!")
