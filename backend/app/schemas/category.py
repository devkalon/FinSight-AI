from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    name: str
    group_type: Optional[str] = "Need"
    icon: Optional[str] = "Tag"
    color: Optional[str] = "#6366F1"

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: str
    user_id: Optional[str] = None
    is_custom: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryRuleCreate(BaseModel):
    keyword_pattern: str
    category_id: str

class CategoryRuleOut(BaseModel):
    id: str
    keyword_pattern: str
    category_id: str
    confidence_score: float
    created_at: datetime

    class Config:
        from_attributes = True

class CategorizeTransactionRequest(BaseModel):
    description: str
    merchant_name: Optional[str] = None

class CategorizeTransactionResponse(BaseModel):
    category: str
    subcategory: str
    confidence: float
    classification_method: str # "user_learned_rule", "deterministic_rule", "ml_classifier", "llm_fallback"
    rationale: str
    is_low_confidence: bool

class CategorizationMetricsResponse(BaseModel):
    total_samples: int
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    f1_weighted: float
    expected_calibration_error: float
    brier_score: float
    is_calibrated: bool

class UserCorrectionRuleRequest(BaseModel):
    merchant_or_pattern: str
    category_id: str
    subcategory: Optional[str] = None
