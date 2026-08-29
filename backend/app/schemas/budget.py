from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.category import CategoryOut

class BudgetBase(BaseModel):
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    monthly_limit: float
    period: Optional[str] = "monthly"
    alert_threshold_percentage: Optional[int] = 80
    warning_threshold_pct: Optional[float] = None

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    monthly_limit: Optional[float] = None
    alert_threshold_percentage: Optional[int] = None

class BudgetPerformanceMonth(BaseModel):
    month: str
    budgeted_limit: float
    spent_amount: float
    adherence_percentage: float
    is_over_budget: bool

class BudgetOut(BudgetBase):
    id: str
    user_id: str
    created_at: datetime
    category: Optional[CategoryOut] = None
    spent_amount: Optional[float] = 0.0
    remaining_amount: Optional[float] = 0.0
    spent_percentage: Optional[float] = 0.0
    is_over_budget: Optional[bool] = False
    warning_status: Optional[str] = "normal" # 'normal', 'warning', 'critical_overbudget'
    warning_message: Optional[str] = None
    historical_performance: Optional[list] = []
    ai_recommendation: Optional[str] = None

    class Config:
        from_attributes = True

class BudgetHistoricalPerformanceResponse(BaseModel):
    total_active_budgets: int
    overall_monthly_limit: float
    overall_spent_amount: float
    overall_adherence_pct: float
    active_warnings_count: int
    monthly_history: list
    category_insights: list
