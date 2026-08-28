from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    full_name: str = Field(..., min_length=2)
    preferred_currency: Optional[str] = "INR"
    preferred_guru: Optional[str] = "balanced"
    monthly_income: Optional[float] = 0.0

    @field_validator("password")
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    preferred_currency: str
    preferred_guru: str
    monthly_income: float
    is_active: bool
    risk_tolerance: Optional[str] = "moderate"
    country_code: Optional[str] = "IN"
    tax_regime: Optional[str] = "new"
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_currency: Optional[str] = None
    preferred_guru: Optional[str] = None
    monthly_income: Optional[float] = None
    risk_tolerance: Optional[str] = None
    tax_regime: Optional[str] = None

class UserPreferences(BaseModel):
    preferred_currency: Optional[str] = "INR"
    preferred_guru: Optional[str] = "balanced"
    risk_tolerance: Optional[str] = "moderate"
    tax_regime: Optional[str] = "new"

class LogoutResponse(BaseModel):
    message: str = "Successfully logged out. Token has been revoked."

class PrivacyDeletionResponse(BaseModel):
    message: str
    deleted_user_id: str
    timestamp: datetime
