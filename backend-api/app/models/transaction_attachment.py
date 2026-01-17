from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TransactionAttachment(Base):
    __tablename__ = "transaction_attachments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # 서버에 저장된 파일 경로
    file_size = Column(Integer, nullable=False)  # 파일 크기 (bytes)
    mime_type = Column(String, nullable=False)  # MIME 타입
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="attachments")
    user = relationship("User")
