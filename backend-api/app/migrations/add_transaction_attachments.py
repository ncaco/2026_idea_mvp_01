"""
거래 첨부파일 테이블 추가 마이그레이션
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
            CREATE TABLE IF NOT EXISTS transaction_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_attachment_transaction_id ON transaction_attachments(transaction_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_attachment_user_id ON transaction_attachments(user_id)"))
        conn.commit()


if __name__ == "__main__":
    upgrade()
    print("거래 첨부파일 테이블이 생성되었습니다.")
