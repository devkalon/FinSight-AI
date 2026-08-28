from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, get_utc_now

class FinancialScore(Base, UUIDMixin):
    __tablename__ = "financial_scores"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    composite_score = Column(Integer, nullable=False) # 0 to 100
    rating = Column(String(50), nullable=False) # 'Excellent', 'Good', 'Fair', 'Needs Attention'
    
    emergency_fund_score = Column(Integer, nullable=False) # max 25
    savings_rate_score = Column(Integer, nullable=False) # max 25
    budget_adherence_score = Column(Integer, nullable=False) # max 25
    debt_and_burn_score = Column(Integer, nullable=False) # max 25
    
    calculation_metadata = Column(JSON, nullable=True) # Insights, ratios, and formula snapshots
    calculated_at = Column(DateTime, default=get_utc_now, nullable=False, index=True)

    user = relationship("User", back_populates="financial_scores")

    __table_args__ = (
        Index("ix_financial_scores_user_time", "user_id", "calculated_at"),
    )
