from datetime import date
from sqlalchemy import Column, String, Boolean, Numeric, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

class Subscription(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "subscriptions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    service_name = Column(String(255), nullable=False) # e.g. "Netflix Premium", "Spotify"
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    billing_cycle = Column(String(50), default="monthly", nullable=False) # 'monthly', 'yearly', 'quarterly', 'weekly'
    recurring_type = Column(String(50), default="monthly_subscription", nullable=False) # 'monthly_subscription', 'annual_subscription', 'recurring_bill', 'recurring_membership'
    confidence = Column(Numeric(4, 2), default=0.90, nullable=False)
    status = Column(String(50), default="confirmed", nullable=False) # 'detected', 'confirmed', 'dismissed'
    last_paid_date = Column(Date, nullable=True)
    next_billing_date = Column(Date, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    user = relationship("User", back_populates="subscriptions")
    merchant = relationship("Merchant")
    category = relationship("Category")

    __table_args__ = (
        Index("ix_subscriptions_user_active", "user_id", "is_active"),
        Index("ix_subscriptions_user_status", "user_id", "status"),
    )
