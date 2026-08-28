from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from backend.app.schemas.category import CategoryOut

class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")
    currency: str = Field(default="INR", max_length=10)
    transaction_type: str = Field(default="debit", description="'debit', 'credit', or 'transfer'")
    transaction_date: date
    description: str
    merchant_name: Optional[str] = None
    category_id: Optional[str] = None
    subcategory: Optional[str] = None
    payment_method: Optional[str] = "UPI"
    source: Optional[str] = "manual"
    confidence_score: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    is_subscription: Optional[bool] = False
    notes: Optional[str] = None
    extra_metadata: Optional[str] = None

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        valid_types = {"debit", "credit", "transfer"}
        if v.lower() not in valid_types:
            raise ValueError(f"transaction_type must be one of {valid_types}")
        return v.lower()

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = None
    transaction_type: Optional[str] = None
    transaction_date: Optional[date] = None
    description: Optional[str] = None
    merchant_name: Optional[str] = None
    category_id: Optional[str] = None
    subcategory: Optional[str] = None
    payment_method: Optional[str] = None
    source: Optional[str] = None
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    is_subscription: Optional[bool] = None
    notes: Optional[str] = None
    extra_metadata: Optional[str] = None

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_types = {"debit", "credit", "transfer"}
            if v.lower() not in valid_types:
                raise ValueError(f"transaction_type must be one of {valid_types}")
            return v.lower()
        return v

class TransactionOut(TransactionBase):
    id: str
    user_id: str
    is_anomaly: Optional[bool] = False
    anomaly_reason: Optional[str] = None
    raw_extracted_text: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CategoryOut] = None

    model_config = {
        "from_attributes": True
    }

class PaginatedTransactionResponse(BaseModel):
    items: List[TransactionOut]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class BatchTransactionCreate(BaseModel):
    transactions: List[TransactionCreate]
