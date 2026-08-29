from decimal import Decimal
from sqlalchemy import Column, String, Boolean, Numeric, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship, synonym
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

class Budget(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "budgets"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(100), default="Monthly Household Budget", nullable=False)
    period = Column(String(20), default="monthly", nullable=False) # 'monthly', 'quarterly', 'yearly'
    total_limit = Column(Numeric(14, 2), nullable=False)
    alert_threshold_percentage = Column(Integer, default=80, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Synonym for backward compatibility
    monthly_limit = synonym("total_limit")

    user = relationship("User", back_populates="budgets")
    category = relationship("Category")
    budget_categories = relationship("BudgetCategory", back_populates="budget", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "monthly_limit" in kwargs and "total_limit" not in kwargs:
            kwargs["total_limit"] = Decimal(str(kwargs.pop("monthly_limit")))
        if "warning_threshold_pct" in kwargs and "alert_threshold_percentage" not in kwargs:
            kwargs["alert_threshold_percentage"] = int(kwargs.pop("warning_threshold_pct"))
        super().__init__(**kwargs)

    __table_args__ = (
        Index("ix_budgets_user_active", "user_id", "is_active"),
    )

class BudgetCategory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "budget_categories"

    budget_id = Column(String(36), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    allocated_limit = Column(Numeric(14, 2), nullable=False)

    budget = relationship("Budget", back_populates="budget_categories")
    category = relationship("Category", back_populates="budget_categories")

    __table_args__ = (
        UniqueConstraint("budget_id", "category_id", name="uq_budget_category"),
    )
