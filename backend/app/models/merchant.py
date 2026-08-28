from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, TimestampMixin

class Merchant(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "merchants"

    name = Column(String(255), nullable=False, index=True)
    normalized_name = Column(String(255), unique=True, nullable=False, index=True) # lowercase trimmed e.g. "swiggy"
    default_category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    icon = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)

    default_category = relationship("Category", foreign_keys=[default_category_id])
    transactions = relationship("Transaction", back_populates="merchant")
