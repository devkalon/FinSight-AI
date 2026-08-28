from sqlalchemy import Column, String, JSON, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, get_utc_now

class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True) # 'user_login', 'transaction_created', 'ocr_processed', 'budget_modified'
    entity_type = Column(String(100), nullable=False, index=True) # 'Transaction', 'Budget', 'FinancialGoal', 'User'
    entity_id = Column(String(36), nullable=True)
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False, index=True)

    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_user_action", "user_id", "action"),
    )
