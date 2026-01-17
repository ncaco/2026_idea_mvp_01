"""
반복 거래 테이블 추가 마이그레이션
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
    """반복 거래 테이블 생성"""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                description TEXT,
                frequency TEXT NOT NULL,
                day_of_month INTEGER,
                day_of_week INTEGER,
                start_date DATE NOT NULL,
                end_date DATE,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                last_generated_date DATE,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_recurring_user_active 
            ON recurring_transactions(user_id, is_active)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_recurring_start_date 
            ON recurring_transactions(start_date)
        """))
        
        conn.commit()


def downgrade():
    """반복 거래 테이블 삭제"""
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS recurring_transactions"))
        conn.commit()


if __name__ == "__main__":
    upgrade()
    print("반복 거래 테이블이 생성되었습니다.")
