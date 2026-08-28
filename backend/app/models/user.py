from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="joined")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    transaction_sources = relationship("TransactionSource", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("FinancialGoal", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("FinancialDocument", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="user", cascade="all, delete-orphan")
    financial_scores = relationship("FinancialScore", back_populates="user", cascade="all, delete-orphan")
    advice_sessions = relationship("AdviceSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    # Delegate properties for convenience and backward compatibility
    @property
    def full_name(self) -> str:
        return self.profile.full_name if self.profile else self.email.split("@")[0]

    @property
    def preferred_currency(self) -> str:
        return self.profile.preferred_currency if self.profile else "INR"

    @property
    def preferred_guru(self) -> str:
        return self.profile.preferred_guru if self.profile else "balanced"

    @property
    def monthly_income(self) -> float:
        return float(self.profile.monthly_income) if self.profile else 0.0

    @property
    def risk_tolerance(self) -> str:
        return self.profile.risk_tolerance if self.profile else "moderate"

    @property
    def country_code(self) -> str:
        return self.profile.country_code if self.profile else "IN"

    @property
    def tax_regime(self) -> str:
        return self.profile.tax_regime if self.profile else "new"

    __table_args__ = (
        Index("ix_users_email_is_active", "email", "is_active"),
    )

class Profile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    preferred_currency = Column(String(10), default="INR", nullable=False)
    monthly_income = Column(Numeric(14, 2), default=0.00, nullable=False)
    risk_tolerance = Column(String(50), default="moderate", nullable=False) # 'conservative', 'moderate', 'aggressive'
    country_code = Column(String(10), default="IN", nullable=False)
    tax_regime = Column(String(50), default="new", nullable=False) # 'new', 'old'
    preferred_guru = Column(String(50), default="balanced", nullable=False)

    user = relationship("User", back_populates="profile")
