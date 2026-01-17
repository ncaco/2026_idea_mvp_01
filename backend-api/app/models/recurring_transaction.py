from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    type = Column(String, nullable=False)  # 'income' or 'expense'
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=True)
    
    # 반복 설정
    frequency = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly', 'yearly'
    day_of_month = Column(Integer, nullable=True)  # 월의 몇 일 (1-31, NULL이면 매월 마지막 날)
    day_of_week = Column(Integer, nullable=True)  # 요일 (0=월요일, 6=일요일, weekly일 때만 사용)
    start_date = Column(Date, nullable=False)  # 반복 시작일
    end_date = Column(Date, nullable=True)  # 반복 종료일 (NULL이면 무제한)
    
    # 상태
    is_active = Column(Boolean, default=True, nullable=False)  # 활성화 여부
    last_generated_date = Column(Date, nullable=True)  # 마지막으로 거래가 생성된 날짜
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="recurring_transactions")
    category = relationship("Category")

    # 인덱스
    __table_args__ = (
        Index("idx_recurring_user_active", "user_id", "is_active"),
        Index("idx_recurring_start_date", "start_date"),
    )
