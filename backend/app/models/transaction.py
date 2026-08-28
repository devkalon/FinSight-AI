from datetime import date
from sqlalchemy import Column, String, Boolean, Numeric, Date, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

class TransactionSource(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "transaction_sources"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_name = Column(String(100), nullable=False) # e.g. "HDFC Salary Account", "PhonePe UPI", "Manual OCR"
    source_type = Column(String(50), nullable=False, index=True) # 'bank_pdf', 'ocr_receipt', 'csv', 'upi_sms', 'manual'
    account_identifier_masked = Column(String(50), nullable=True) # e.g. "XX-4091"
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="transaction_sources")
    transactions = relationship("Transaction", back_populates="transaction_source")

class Transaction(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "transactions"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(36), ForeignKey("transaction_sources.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id", ondelete="SET NULL"), nullable=True, index=True)
    merchant_name = Column(String(255), nullable=True, index=True)
    
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    transaction_type = Column(String(20), default="debit", nullable=False, index=True) # 'debit', 'credit', 'transfer'
    transaction_date = Column(Date, default=date.today, nullable=False, index=True)
    description = Column(Text, nullable=False)
    subcategory = Column(String(100), nullable=True)
    payment_method = Column(String(50), default="UPI", nullable=False, index=True) # 'UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Cash'
    source = Column(String(50), default="manual", nullable=True, index=True)
    
    confidence_score = Column(Numeric(5, 4), default=1.0000, nullable=False) # e.g. 0.9450 for OCR
    is_subscription = Column(Boolean, default=False, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    extra_metadata = Column(Text, nullable=True)
    raw_extracted_text = Column(Text, nullable=True)

    user = relationship("User", back_populates="transactions")
    transaction_source = relationship("TransactionSource", back_populates="transactions", foreign_keys=[source_id])
    category = relationship("Category", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
    anomalies = relationship("Anomaly", back_populates="transaction", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "transaction_date"),
        Index("ix_transactions_user_type", "user_id", "transaction_type"),
        Index("ix_transactions_user_category", "user_id", "category_id"),
        Index("ix_transactions_user_merchant", "user_id", "merchant_name"),
        Index("ix_transactions_user_active_date", "user_id", "is_deleted", "transaction_date"),
        Index("ix_transactions_user_active_type_date", "user_id", "is_deleted", "transaction_type", "transaction_date"),
    )
