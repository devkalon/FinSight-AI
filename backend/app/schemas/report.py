from datetime import date, datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class MonthlyReportMetrics(BaseModel):
    month: str # e.g. "2026-08"
    month_name: str # e.g. "August 2026"
    currency: str = "INR"
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate_pct: float
    average_daily_spending: float
    essential_spending: float
    discretionary_spending: float
    spending_by_category: List[Dict[str, Any]]
    top_merchants: List[Dict[str, Any]]
    total_budget_limit: float
    budget_utilization_pct: float
    overbudget_categories_count: int
    budget_items: List[Dict[str, Any]]
    active_goals_count: int
    total_goal_target: float
    total_goal_saved: float
    goals: List[Dict[str, Any]]
    anomalies_detected_count: int
    anomalies: List[Dict[str, Any]]
    recurring_monthly_total: float
    recurring_annual_total: float
    recurring_items: List[Dict[str, Any]]
    forecast_next_30_days: float
    forecast_confidence: float
    health_score: int
    health_rating: str

class MonthlyReportNarrative(BaseModel):
    executive_summary: str
    income_narrative: str
    spending_narrative: str
    savings_narrative: str
    budget_narrative: str
    goal_narrative: str
    anomalies_narrative: str
    recurring_narrative: str
    forecast_narrative: str
    key_observations: List[str]
    recommended_actions: List[str]

class MonthlyReportResponse(BaseModel):
    report_id: str
    month: str
    generated_at: str
    user_name: str
    metrics: MonthlyReportMetrics
    narrative: MonthlyReportNarrative
