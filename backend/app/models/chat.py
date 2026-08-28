from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, get_utc_now

class ChatSession(Base, UUIDMixin):
    __tablename__ = "chat_sessions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="Financial Advisory Consultation", nullable=False)
    persona = Column(String(50), default="balanced", nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base, UUIDMixin):
    __tablename__ = "chat_messages"

    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False) # 'user', 'assistant', 'tool', 'system'
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)
    citations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    session = relationship("ChatSession", back_populates="messages")
