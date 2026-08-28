from typing import List, Dict, Any, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

class HealthScoreComponentDetail(BaseModel):
    name: str
    score: int # 0 to 100
    weight: float # e.g. 0.20
    weighted_score: float
    status: str # 'Excellent', 'Good', 'Fair', 'Needs Attention'
    metric_value: str # e.g. "32.5%", "4.5 months", "12% DTI"
    description: str

class HealthScoreDetailResponse(BaseModel):
    score: int # 0 to 100
    rating: str # 'Excellent', 'Good', 'Fair', 'Needs Attention'
    components: Dict[str, HealthScoreComponentDetail]
    positive_factors: List[str]
    negative_factors: List[str]
    recommendations: List[str]
    score_delta: Optional[int] = 0
    delta_explanation: Optional[str] = None
    calculated_at: Optional[str] = None

    # Backward compatibility fields
    emergency_fund_score: Optional[int] = 0
    savings_rate_score: Optional[int] = 0
    budget_adherence_score: Optional[int] = 0
    debt_and_burn_score: Optional[int] = 0
    insights: Optional[List[str]] = []

# Alias for backward compatibility
HealthScoreBreakdown = HealthScoreDetailResponse

class HealthScoreHistoryPoint(BaseModel):
    id: str
    score: int
    rating: str
    calculated_at: str
    component_scores: Dict[str, int]

class HealthScoreHistoryResponse(BaseModel):
    history: List[HealthScoreHistoryPoint]

class CashFlowPoint(BaseModel):
    month: str # e.g. "2026-05" or "May 2026"
    income: float
    expense: float
    savings: float
    savings_rate_pct: float

class CategorySpending(BaseModel):
    category_id: Optional[str] = None
    category_name: str
    group_type: str # 'Need', 'Want', 'Savings', 'Investment'
    total_amount: float
    percentage_of_total: float
    transaction_count: int
    color: str

class FinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate_pct: float
    average_daily_spending: float
    days_in_period: int
    transaction_count: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    currency: str = "INR"

class MonthOverMonthChange(BaseModel):
    income_change_pct: float
    expense_change_pct: float
    savings_change_pct: float
    income_change_abs: float
    expense_change_abs: float
    savings_change_abs: float
    prev_period_income: float
    prev_period_expense: float
    prev_period_savings: float

class SpendingSplit(BaseModel):
    essential_amount: float # Needs (Rent, Bills, Food/Groceries, EMI, Healthcare, Insurance)
    essential_pct: float
    discretionary_amount: float # Wants (Shopping, Dining, Entertainment, Travel, Subscriptions)
    discretionary_pct: float
    savings_investment_amount: float # Investments & Savings
    savings_investment_pct: float

class TopMerchantSpending(BaseModel):
    merchant_name: str
    total_amount: float
    transaction_count: int
    percentage_of_expenses: float

class BudgetUtilizationItem(BaseModel):
    category_id: Optional[str] = None
    category_name: str
    budgeted_amount: float
    spent_amount: float
    utilization_pct: float
    remaining_amount: float
    is_over_budget: bool
    color: str = "#6366F1"

class ComprehensiveAnalyticsDashboard(BaseModel):
    summary: FinancialSummary
    month_over_month: MonthOverMonthChange
    spending_split: SpendingSplit
    category_breakdown: List[CategorySpending]
    income_vs_expense_trends: List[CashFlowPoint]
    largest_merchants: List[TopMerchantSpending]
    budget_utilization: List[BudgetUtilizationItem]
    recurring_expenses: List["SubscriptionItem"]

class AffectedTransactionDetail(BaseModel):
    id: str
    description: str
    amount: float
    merchant: Optional[str] = None
    transaction_date: date
    category_name: Optional[str] = None

class DetailedAnomalyOut(BaseModel):
    id: str
    anomaly_type: str # 'category_spending', 'merchant_spending', 'transaction_amount', 'frequency_spike', 'recurring_change', 'monthly_spending'
    severity: str # 'critical', 'high', 'medium', 'low'
    metric: str # e.g. 'category_monthly_total', 'merchant_burn_rate', 'single_transaction', 'daily_frequency', 'recurring_charge_step', 'monthly_total'
    entity_name: str # e.g. "Food", "Swiggy", "Netflix Subscription", "Overall Monthly Spend"
    observed_value: float
    expected_value: float
    deviation: str # e.g. "+155.0%"
    deviation_pct: float
    explanation: str
    affected_transactions: List[AffectedTransactionDetail] = []
    detected_at: datetime

class AnomalySummaryResponse(BaseModel):
    total_anomalies: int
    critical_count: int
    high_count: int
    medium_count: int
    total_excess_deviation: float
    has_sufficient_history: bool
    message: Optional[str] = None
    anomalies: List[DetailedAnomalyOut]

class AnomalyItem(BaseModel):
    transaction_id: str
    description: str
    amount: float
    transaction_date: date
    category_name: Optional[str] = None
    reason: str
    severity: str # 'high', 'medium', 'info'

class SubscriptionItem(BaseModel):
    id: Optional[str] = None
    service_name: str
    amount: float
    billing_cycle: str
    next_billing_date: date
    category_name: Optional[str] = None
    is_active: bool

class PredictionInterval(BaseModel):
    lower_bound: float
    upper_bound: float
    confidence_level: float = 0.85

class CategoryForecastItem(BaseModel):
    category_name: str
    predicted_amount: float
    prediction_interval: PredictionInterval
    percentage_of_total: float
    trend: str # 'increasing', 'stable', 'decreasing'
    contributing_factors: List[str] = []

class RecurringForecastItem(BaseModel):
    service_name: str
    amount: float
    billing_cycle: str
    projected_annual_cost: float
    category_name: Optional[str] = None
    next_billing_date: Optional[str] = None

class ModelEvaluationMetrics(BaseModel):
    model_name: str
    baseline_model_name: str
    mae: float
    mape: float # in %
    rmse: float
    baseline_mae: float
    baseline_mape: float
    baseline_rmse: float
    accuracy_improvement_pct: float
    evaluation_holdout_days: int

class ForecastPoint(BaseModel):
    date: str
    projected_expense: float
    lower_bound: float
    upper_bound: float

class ForecastResponse(BaseModel):
    predicted_monthly_total: float
    monthly_prediction_interval: PredictionInterval
    confidence_score: float
    historical_average_daily: float
    projected_next_30_days_total: float
    projected_next_60_days_total: float
    projected_next_90_days_total: float
    estimated_runway_months: float
    trend: str # 'increasing', 'decreasing', 'stable'
    major_contributing_factors: List[str] = []
    human_readable_explanation: str
    disclaimer: str
    category_forecasts: List[CategoryForecastItem] = []
    recurring_forecasts: List[RecurringForecastItem] = []
    total_recurring_projected: float = 0.0
    total_variable_projected: float = 0.0
    evaluation: Optional[ModelEvaluationMetrics] = None
    forecast_points: List[ForecastPoint] = []

class SimulationRequest(BaseModel):
    monthly_income_change: Optional[float] = 0.0
    income_change_pct: Optional[float] = 0.0
    monthly_expense_reduction: Optional[float] = 0.0
    food_spend_reduction: Optional[float] = 0.0
    shopping_spend_reduction: Optional[float] = 0.0
    discretionary_spend_reduction: Optional[float] = 0.0
    removed_subscriptions_amount: Optional[float] = 0.0
    extra_goal_contribution: Optional[float] = 0.0
    budget_limit_change: Optional[float] = 0.0
    one_time_purchase_amount: Optional[float] = 0.0
    inflation_rate: Optional[float] = 6.0 # % annual
    investment_roi: Optional[float] = 12.0 # % annual
    timeline_months: Optional[int] = 24

class ScenarioMetricsOut(BaseModel):
    monthly_income: float
    monthly_expenses: float
    monthly_net_cash_flow: float
    savings_rate_pct: float
    annual_savings: float
    total_budget_limit: float
    budget_utilization_pct: float
    health_score: int
    health_rating: str

class GoalImpactItemOut(BaseModel):
    goal_title: str
    target_amount: float
    current_amount: float
    remaining_amount: float
    baseline_months_to_complete: int
    simulated_months_to_complete: int
    months_saved: int
    accelerated_completion_date: str

class SimulationResponse(BaseModel):
    current_scenario: Optional[ScenarioMetricsOut] = None
    simulated_scenario: Optional[ScenarioMetricsOut] = None
    net_monthly_delta: Optional[float] = 0.0
    annual_savings_delta: Optional[float] = 0.0
    health_score_delta: Optional[int] = 0
    budget_utilization_delta_pct: Optional[float] = 0.0
    goal_impacts: Optional[List[GoalImpactItemOut]] = []
    simulated_timeline: List[Dict[str, Any]]
    projected_net_savings: float
    runway_impact_months: float
    ai_explanation: Optional[str] = None
    guru_critique: Dict[str, str]
