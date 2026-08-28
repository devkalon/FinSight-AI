from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class CandidateTransaction(BaseModel):
    id: Optional[str] = None
    description: str
    merchant_name: Optional[str] = None
    amount: float = Field(..., gt=0)
    currency: str = "INR"
    transaction_type: str = "debit"
    transaction_date: str
    category_suggestion: Optional[str] = None
    subcategory: Optional[str] = None
    payment_method: Optional[str] = "UPI"
    source: str = "ocr_receipt"
    confidence_score: float = 0.90
    raw_text: Optional[str] = None
    fingerprint: Optional[str] = None
    reference_number: Optional[str] = None
    is_duplicate: bool = False
    duplicate_reason: Optional[str] = None
    is_confirmed: bool = False

class DocumentOut(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    processing_status: str
    parsed_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ExtractedReceiptTransaction(BaseModel):
    merchant_name: Optional[str] = "Unknown Merchant"
    amount: float = 0.0
    currency: str = "INR"
    transaction_date: str
    category_suggestion: Optional[str] = "Shopping"
    subcategory: Optional[str] = None
    payment_method: Optional[str] = "UPI"
    raw_text: Optional[str] = ""
    confidence_score: float = 0.85
    redaction_stats: Optional[Dict[str, int]] = {}

class OCRUploadResponse(BaseModel):
    document_id: str
    filename: str
    extracted_transaction: ExtractedReceiptTransaction
    candidates: List[CandidateTransaction] = []

class BankStatementParseResponse(BaseModel):
    document_id: str
    filename: str
    total_parsed_transactions: int
    transactions: List[Dict[str, Any]]
    candidates: List[CandidateTransaction] = []
    account_summary: Optional[Dict[str, Any]] = None

class DocumentIngestionResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    processing_status: str
    total_extracted_transactions: int
    confidence_avg: float
    candidates: List[CandidateTransaction] = []
    redaction_stats: Optional[Dict[str, int]] = {}
    account_summary: Optional[Dict[str, Any]] = None

class ConfirmCandidatesRequest(BaseModel):
    transactions: List[CandidateTransaction]

class ConfirmCandidatesResponse(BaseModel):
    document_id: str
    committed_count: int
    transaction_ids: List[str]
    message: str

class KnowledgeChunkOut(BaseModel):
    id: Optional[str] = None
    document_id: Optional[str] = None
    chunk_index: Optional[int] = 0
    page_number: Optional[int] = 1
    content: Optional[str] = None
    relevant_quote: Optional[str] = None
    source_title: str
    author: Optional[str] = None
    relevance_score: float
    is_user_doc: Optional[bool] = False

class KnowledgeDocumentOut(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size_bytes: int
    total_chunks: int
    source_title: str
    author: Optional[str] = None
    created_at: datetime

class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    relevance_threshold: Optional[float] = 0.20

class KnowledgeSearchResponse(BaseModel):
    query: str
    results_count: int
    chunks: List[KnowledgeChunkOut]
    answer_supported: bool
    grounded_summary: Optional[str] = None
