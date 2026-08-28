from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

class FinancialDocument(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "financial_documents"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False, index=True) # 'receipt', 'bank_statement_pdf', 'bank_statement_csv', 'financial_book'
    file_size_bytes = Column(Integer, default=0, nullable=False)
    storage_path = Column(Text, nullable=False)
    processing_status = Column(String(50), default="processed", nullable=False, index=True) # 'pending', 'processing', 'processed', 'failed'
    parsed_metadata = Column(JSON, nullable=True)

    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_financial_docs_user_type", "user_id", "file_type"),
    )

class DocumentChunk(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document_chunks"

    document_id = Column(String(36), ForeignKey("financial_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)

    document = relationship("FinancialDocument", back_populates="chunks")

    __table_args__ = (
        Index("ix_doc_chunks_doc_index", "document_id", "chunk_index"),
    )

# Backward-compatibility alias
Document = FinancialDocument
