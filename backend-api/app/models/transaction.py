from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # 'income' or 'expense'
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=True)
    transaction_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    tags = relationship("Tag", secondary="transaction_tags", back_populates="transactions")
    attachments = relationship("TransactionAttachment", back_populates="transaction", cascade="all, delete-orphan")

    # 인덱스
    __table_args__ = (
        Index("idx_transaction_date", "transaction_date"),
        Index("idx_user_transaction_date", "user_id", "transaction_date"),
    )
