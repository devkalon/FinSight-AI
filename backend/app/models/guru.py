from sqlalchemy import Column, String, Boolean, Integer, Numeric, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, TimestampMixin

class GuruProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "guru_profiles"

    guru_code = Column(String(50), unique=True, nullable=False, index=True) # 'buffett', 'kiyosaki', 'sethi', 'indian_expert'
    name = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    core_mantra = Column(Text, nullable=False)
    philosophy_description = Column(Text, nullable=False)
    avatar_url = Column(String(255), nullable=True)

    principles = relationship("GuruPrinciple", back_populates="guru", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="guru")
    advice_sessions = relationship("AdviceSession", back_populates="guru")

class GuruPrinciple(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "guru_principles"

    guru_id = Column(String(36), ForeignKey("guru_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    principle_order = Column(Integer, default=1, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    guru = relationship("GuruProfile", back_populates="principles")

class AdviceSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "advice_sessions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    guru_id = Column(String(36), ForeignKey("guru_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), default="Financial Strategy Consultation", nullable=False)
    session_type = Column(String(50), default="chat", nullable=False) # 'chat', 'portfolio_review', 'budget_audit'
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="advice_sessions")
    guru = relationship("GuruProfile", back_populates="advice_sessions")
    recommendations = relationship("Recommendation", back_populates="session", cascade="all, delete-orphan")

class Recommendation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recommendations"

    session_id = Column(String(36), ForeignKey("advice_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    guru_id = Column(String(36), ForeignKey("guru_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)

    topic = Column(String(255), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    action_items = Column(JSON, nullable=True) # List of concrete action points
    estimated_savings_impact = Column(Numeric(14, 2), default=0.00, nullable=False)

    session = relationship("AdviceSession", back_populates="recommendations")
    user = relationship("User")
    guru = relationship("GuruProfile", back_populates="recommendations")
    category = relationship("Category")
