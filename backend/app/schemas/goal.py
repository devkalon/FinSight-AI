from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel

class GoalBase(BaseModel):
    title: str
    category: Optional[str] = "Wealth Creation"
    target_amount: float
    current_amount: Optional[float] = 0.0
    target_date: date
    expected_return_rate: Optional[float] = 12.0
    monthly_contribution: Optional[float] = 0.0

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    target_date: Optional[date] = None
    expected_return_rate: Optional[float] = None
    monthly_contribution: Optional[float] = None
    status: Optional[str] = None

class GoalContribute(BaseModel):
    amount: float

class GoalOut(GoalBase):
    id: str
    user_id: str
    status: str
    progress_percentage: Optional[float] = 0.0
    remaining_amount: Optional[float] = 0.0
    months_remaining: Optional[int] = 0
    required_monthly_saving: Optional[float] = 0.0
    required_monthly_sip: Optional[float] = 0.0
    projected_completion_date: Optional[str] = None
    is_on_track: Optional[bool] = True
    ai_recommendation: Optional[str] = None
    projected_corpus_at_maturity: Optional[float] = 0.0
    created_at: datetime

    class Config:
        from_attributes = True
