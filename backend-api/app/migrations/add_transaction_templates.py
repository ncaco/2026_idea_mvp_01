"""
거래 템플릿 테이블 추가 마이그레이션
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'accountbook.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def upgrade():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS transaction_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                description TEXT,
                name TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_template_user_id ON transaction_templates(user_id)"))
        conn.commit()


if __name__ == "__main__":
    upgrade()
    print("거래 템플릿 테이블이 생성되었습니다.")
