from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class SubscriptionBase(BaseModel):
    service_name: str
    amount: float
    billing_cycle: Optional[str] = "monthly"
    recurring_type: Optional[str] = "monthly_subscription"
    next_billing_date: Optional[date] = None
    category_id: Optional[str] = None

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    service_name: Optional[str] = None
    amount: Optional[float] = None
    billing_cycle: Optional[str] = None
    recurring_type: Optional[str] = None
    next_billing_date: Optional[date] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class SubscriptionOut(BaseModel):
    id: str
    user_id: str
    service_name: str
    amount: float
    currency: str = "INR"
    billing_cycle: str
    recurring_type: str
    annualized_cost: float
    confidence: float
    status: str
    last_paid_date: Optional[date] = None
    next_billing_date: date
    is_active: bool
    category_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SubscriptionDashboardResponse(BaseModel):
    total_monthly_recurring: float
    total_annual_recurring: float
    active_subscriptions_count: int
    pending_detection_count: int
    subscriptions_by_type: Dict[str, float]
    subscriptions: List[SubscriptionOut]
