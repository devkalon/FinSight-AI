from sqlalchemy import Column, String, Boolean, Float, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

class Category(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categories"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    group_type = Column(String(50), default="Need", nullable=False) # 'Need', 'Want', 'Savings', 'Investment', 'Income'
    icon = Column(String(50), default="Tag", nullable=False)
    color = Column(String(20), default="#6366F1", nullable=False)
    is_custom = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budget_categories = relationship("BudgetCategory", back_populates="category")
    rules = relationship("CategoryRule", back_populates="category", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_categories_user_id_group", "user_id", "group_type"),
        UniqueConstraint("user_id", "name", name="uq_user_category_name"),
    )

class CategoryRule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "category_learning_rules"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword_pattern = Column(String(255), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    confidence_score = Column(Float, default=1.0, nullable=False)

    user = relationship("User")
    category = relationship("Category", back_populates="rules")

    __table_args__ = (
        Index("ix_category_rules_user_keyword", "user_id", "keyword_pattern"),
    )
