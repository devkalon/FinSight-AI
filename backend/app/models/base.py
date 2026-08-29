import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class UUIDMixin:
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)

class TimestampMixin:
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
