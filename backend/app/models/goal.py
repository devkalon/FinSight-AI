from datetime import date
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Date, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

class FinancialGoal(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "financial_goals"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="Wealth Creation", nullable=False) # 'Emergency Fund', 'Retirement', 'Home', 'Vacation', 'Vehicle'
    target_amount = Column(Numeric(14, 2), nullable=False)
    current_amount = Column(Numeric(14, 2), default=0.00, nullable=False)
    monthly_contribution = Column(Numeric(14, 2), default=0.00, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    target_date = Column(Date, nullable=False, index=True)
    expected_return_rate = Column(Numeric(5, 2), default=12.00, nullable=False) # e.g. 12.00%
    status = Column(String(50), default="in_progress", nullable=False, index=True) # 'in_progress', 'achieved', 'paused'

    user = relationship("User", back_populates="goals")
    contributions = relationship("GoalContribution", back_populates="goal", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "monthly_contribution" in kwargs and kwargs["monthly_contribution"] is not None:
            kwargs["monthly_contribution"] = Decimal(str(kwargs["monthly_contribution"]))
        if "target_amount" in kwargs and kwargs["target_amount"] is not None:
            kwargs["target_amount"] = Decimal(str(kwargs["target_amount"]))
        if "current_amount" in kwargs and kwargs["current_amount"] is not None:
            kwargs["current_amount"] = Decimal(str(kwargs["current_amount"]))
        super().__init__(**kwargs)

    __table_args__ = (
        Index("ix_financial_goals_user_status", "user_id", "status"),
    )

class GoalContribution(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "goal_contributions"

    goal_id = Column(String(36), ForeignKey("financial_goals.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(14, 2), nullable=False)
    contribution_date = Column(Date, default=date.today, nullable=False)
    notes = Column(Text, nullable=True)

    goal = relationship("FinancialGoal", back_populates="contributions")
    user = relationship("User")
    transaction = relationship("Transaction")
