from sqlalchemy import Column, String, Boolean, Numeric, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, TimestampMixin

class Anomaly(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "anomalies"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    anomaly_type = Column(String(50), default="spend_spike", nullable=False, index=True) # 'spend_spike', 'duplicate_charge', 'frequency_outlier'
    severity = Column(String(20), default="medium", nullable=False, index=True) # 'high', 'medium', 'info'
    description = Column(Text, nullable=False)
    z_score = Column(Numeric(6, 3), default=0.000, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)

    user = relationship("User", back_populates="anomalies")
    transaction = relationship("Transaction", back_populates="anomalies")

    __table_args__ = (
        Index("ix_anomalies_user_unresolved", "user_id", "is_resolved"),
    )
