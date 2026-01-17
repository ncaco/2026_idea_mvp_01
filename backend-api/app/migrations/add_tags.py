"""
태그 및 거래-태그 관계 테이블 추가 마이그레이션
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine

# 데이터베이스 파일 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'accountbook.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def upgrade():
    """태그 테이블 및 거래-태그 관계 테이블 생성"""
    with engine.connect() as conn:
        # tags 테이블 생성
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                color TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, name)
            )
        """))
        
        # transaction_tags 관계 테이블 생성
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS transaction_tags (
                transaction_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (transaction_id, tag_id),
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """))
        
        # 인덱스 생성
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_tags_user_id 
            ON tags(user_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transaction_tags_transaction_id 
            ON transaction_tags(transaction_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transaction_tags_tag_id 
            ON transaction_tags(tag_id)
        """))
        
        conn.commit()


def downgrade():
    """태그 테이블 및 관계 테이블 삭제"""
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS transaction_tags"))
        conn.execute(text("DROP TABLE IF EXISTS tags"))
        conn.commit()


if __name__ == "__main__":
    upgrade()
    print("태그 테이블이 생성되었습니다.")
