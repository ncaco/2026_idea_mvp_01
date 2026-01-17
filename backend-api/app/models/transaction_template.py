from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TransactionTemplate(Base):
    __tablename__ = "transaction_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    type = Column(String, nullable=False)  # 'income' or 'expense'
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=True)
    name = Column(String, nullable=False)  # 템플릿 이름
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="transaction_templates")
    category = relationship("Category")
