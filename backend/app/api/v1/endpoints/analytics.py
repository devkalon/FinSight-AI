from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.category import Category, CategoryRule
from backend.app.models.budget import Budget
from backend.app.models.goal import FinancialGoal
from backend.app.schemas.analytics import (
    HealthScoreBreakdown,
    HealthScoreDetailResponse,
    HealthScoreHistoryPoint,
    HealthScoreHistoryResponse,
    CashFlowPoint,
    CategorySpending,
    AnomalyItem,
    DetailedAnomalyOut,
    AnomalySummaryResponse,
    SubscriptionItem,
    ForecastResponse,
    ModelEvaluationMetrics,
    SimulationRequest,
    SimulationResponse,
    FinancialSummary,
    MonthOverMonthChange,
    SpendingSplit,
    TopMerchantSpending,
    BudgetUtilizationItem,
    ComprehensiveAnalyticsDashboard
)
from backend.app.schemas.category import (
    CategorizeTransactionRequest,
    CategorizeTransactionResponse,
    CategorizationMetricsResponse,
    UserCorrectionRuleRequest,
    CategoryRuleOut
)
from backend.app.services.financial_health import financial_health_engine
from backend.app.services.financial_analytics import financial_analytics_engine
from backend.app.services.ml.anomaly_detector import anomaly_detector
from backend.app.services.ml.forecaster import expense_forecaster
from backend.app.services.ml.subscription_tracker import subscription_tracker
from backend.app.services.ml.categorizer import expense_categorizer
from backend.app.services.ai.tools import financial_tools
from backend.app.api.deps import get_current_user

router = APIRouter()

# =========================================================================
# Deterministic Financial Analytics Endpoints
# =========================================================================

@router.get("/summary", response_model=FinancialSummary)
async def get_financial_summary(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Computes deterministic financial summary KPIs from database transactions.
    """
    return await financial_analytics_engine.calculate_summary(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        currency=current_user.preferred_currency or "INR"
    )

@router.get("/dashboard", response_model=ComprehensiveAnalyticsDashboard)
async def get_comprehensive_analytics_dashboard(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns complete deterministic analytics package for the Next.js financial dashboard.
    """
    return await financial_analytics_engine.get_comprehensive_dashboard(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/month-over-month", response_model=MonthOverMonthChange)
async def get_month_over_month(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculates Month-over-Month % and absolute shifts.
    """
    return await financial_analytics_engine.calculate_month_over_month(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/spending-split", response_model=SpendingSplit)
async def get_spending_split(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Computes Essential (Needs) vs Discretionary (Wants) vs Savings/Investment split.
    """
    return await financial_analytics_engine.calculate_spending_split(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/top-merchants", response_model=List[TopMerchantSpending])
async def get_top_merchants(
    limit: int = Query(5, ge=1, le=50),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves largest merchants ranked by spending volume.
    """
    return await financial_analytics_engine.calculate_top_merchants(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

@router.get("/budget-utilization", response_model=List[BudgetUtilizationItem])
async def get_budget_utilization(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves category-level actual spend vs budgeted limits.
    """
    return await financial_analytics_engine.calculate_budget_utilization(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/trends", response_model=List[CashFlowPoint])
async def get_analytics_trends(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves historical cashflow timeseries.
    """
    return await financial_analytics_engine.calculate_trends(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

# =========================================================================
# Preserved Auxiliary Endpoints
# =========================================================================

@router.get("/health-score", response_model=HealthScoreDetailResponse)
async def get_health_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns explainable 7-factor Financial Health Score with positive/negative factors, recommendations, and delta explanation.
    """
    return await financial_health_engine.compute_health_score(db, current_user.id)

@router.get("/health-score/history", response_model=HealthScoreHistoryResponse)
async def get_health_score_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves historical financial health score progression.
    """
    return await financial_health_engine.get_history(db, current_user.id, limit=limit)

@router.get("/cashflow", response_model=List[CashFlowPoint])
async def get_cashflow_trends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await financial_analytics_engine.calculate_trends(db=db, user_id=current_user.id)

@router.get("/categories", response_model=List[CategorySpending])
async def get_category_spending(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await financial_analytics_engine.calculate_category_spending(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/subscriptions", response_model=List[SubscriptionItem])
async def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.is_deleted == False
        )
    )
    txs = res.scalars().all()
    tx_dicts = [{"description": t.description, "amount": t.amount} for t in txs]
    return subscription_tracker.detect_subscriptions(tx_dicts)


from backend.app.services.financial_simulator import financial_simulator

@router.post("/simulation", response_model=SimulationResponse)
async def simulate_scenario(
    sim_req: SimulationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes a deterministic What-If financial simulation:
    - Calculates cash flow, annual savings, budget headroom, and goal acceleration
    - Compares Current Scenario vs Simulated Scenario
    - Provides post-simulation AI explanation based strictly on calculated results
    """
    # Fetch active user goals
    g_res = await db.execute(
        select(FinancialGoal).filter(
            FinancialGoal.user_id == current_user.id,
            FinancialGoal.status != "achieved"
        )
    )
    goals_db = g_res.scalars().all()
    goals_dicts = [
        {
            "title": g.title,
            "target_amount": float(g.target_amount),
            "current_amount": float(g.current_amount),
            "monthly_saving": float(g.monthly_contribution or (float(g.target_amount) / 12.0))
        }
        for g in goals_db
    ]

    base_income = float(current_user.monthly_income or 75000.0)
    base_expense = max(35000.0 - (sim_req.monthly_expense_reduction or 0.0), 10000.0)

    return financial_simulator.run_simulation(
        base_income=base_income,
        base_expenses=base_expense,
        base_balance=150000.0,
        income_change_pct=sim_req.income_change_pct or 0.0,
        income_change_abs=sim_req.monthly_income_change or 0.0,
        food_spend_reduction=sim_req.food_spend_reduction or 0.0,
        shopping_spend_reduction=sim_req.shopping_spend_reduction or 0.0,
        discretionary_spend_reduction=sim_req.discretionary_spend_reduction or 0.0,
        removed_subscriptions_amount=sim_req.removed_subscriptions_amount or 0.0,
        extra_goal_contribution=sim_req.extra_goal_contribution or 0.0,
        one_time_purchase_amount=sim_req.one_time_purchase_amount or 0.0,
        budget_limit_change=sim_req.budget_limit_change or 0.0,
        inflation_rate=sim_req.inflation_rate or 6.0,
        investment_roi=sim_req.investment_roi or 12.0,
        timeline_months=sim_req.timeline_months or 24,
        active_goals=goals_dicts if goals_dicts else None,
        currency=current_user.preferred_currency or "INR"
    )

# =========================================================================
# Expense Categorization Endpoints
# =========================================================================

@router.post("/categorize", response_model=CategorizeTransactionResponse)
async def categorize_transaction(
    payload: CategorizeTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    r_res = await db.execute(
        select(CategoryRule).options(selectinload(CategoryRule.category)).filter(
            CategoryRule.user_id == current_user.id
        )
    )
    user_rules_db = r_res.scalars().all()
    user_rules = [
        {
            "keyword_pattern": r.keyword_pattern,
            "category_name": r.category.name if r.category else "Other",
            "confidence_score": r.confidence_score
        }
        for r in user_rules_db
    ]

    result = expense_categorizer.predict(
        description=payload.description,
        user_rules=user_rules,
        merchant_name=payload.merchant_name
    )
    return result

@router.get("/categorization-metrics", response_model=CategorizationMetricsResponse)
async def get_categorization_evaluation_metrics():
    return expense_categorizer.evaluate()

@router.post("/categories/learn-rule", response_model=CategoryRuleOut)
async def learn_user_category_rule(
    payload: UserCorrectionRuleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    c_res = await db.execute(
        select(Category).filter(
            Category.id == payload.category_id,
            (Category.user_id == current_user.id) | (Category.user_id == None) | (Category.is_custom == False)
        )
    )
    category = c_res.scalars().first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    pattern_clean = payload.merchant_or_pattern.strip().lower()

    r_res = await db.execute(
        select(CategoryRule).filter(
            CategoryRule.user_id == current_user.id,
            CategoryRule.keyword_pattern == pattern_clean
        )
    )
    existing_rule = r_res.scalars().first()
    if existing_rule:
        existing_rule.category_id = payload.category_id
        existing_rule.confidence_score = 1.0
        await db.commit()
        await db.refresh(existing_rule)
        return existing_rule

    new_rule = CategoryRule(
        user_id=current_user.id,
        keyword_pattern=pattern_clean,
        category_id=payload.category_id,
        confidence_score=1.0
    )
    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)
    return new_rule

# =========================================================================
# Multi-Dimensional Financial Anomaly Detection Endpoints
# =========================================================================

@router.get("/anomalies", response_model=AnomalySummaryResponse)
async def get_detected_financial_anomalies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes statistical and ML anomaly detection across:
    - Category spending surges (e.g. Food +155%)
    - Merchant spending surges
    - Individual transaction amount outliers
    - Frequency burst spikes
    - Recurring subscription price hikes
    - Monthly spending surges
    """
    # Fetch all user debit transactions
    t_res = await db.execute(
        select(Transaction)
        .options(selectinload(Transaction.category))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.is_deleted == False
        )
        .order_by(Transaction.transaction_date.asc())
    )
    tx_models = t_res.scalars().all()

    tx_dicts = [
        {
            "id": t.id,
            "description": t.description or t.merchant_name or "",
            "merchant": t.merchant_name or t.description or "",
            "amount": float(t.amount),
            "transaction_type": str(t.transaction_type),
            "transaction_date": t.transaction_date,
            "category_name": t.category.name if t.category else "Other"
        }
        for t in tx_models
    ]

    return anomaly_detector.detect_detailed_anomalies(
        transactions=tx_dicts,
        currency=current_user.preferred_currency or "INR"
    )

@router.post("/anomalies/scan", response_model=AnomalySummaryResponse)
async def scan_and_detect_anomalies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers a fresh real-time anomaly detection scan on user transactions.
    """
    return await get_detected_financial_anomalies(current_user=current_user, db=db)


# =========================================================================
# Expense Forecasting & Model Evaluation Endpoints
# =========================================================================

@router.get("/forecast", response_model=ForecastResponse)
async def get_expense_forecast(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates multi-horizon probabilistic expense forecast across:
    - Total monthly expenses with 85% prediction intervals
    - Category-level expense projections
    - Recurring fixed commitments & subscription baseline
    - Holdout model evaluation benchmark (MAE, MAPE, RMSE)
    - Plain-English explanation and non-guaranteed statistical disclaimer
    """
    t_res = await db.execute(
        select(Transaction)
        .options(selectinload(Transaction.category))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.is_deleted == False
        )
        .order_by(Transaction.transaction_date.asc())
    )
    tx_models = t_res.scalars().all()

    tx_dicts = [
        {
            "id": t.id,
            "description": t.description or t.merchant_name or "",
            "merchant": t.merchant_name or t.description or "",
            "amount": float(t.amount),
            "transaction_type": str(t.transaction_type),
            "transaction_date": t.transaction_date,
            "category_name": t.category.name if t.category else "Other"
        }
        for t in tx_models
    ]

    return expense_forecaster.generate_forecast(
        transactions=tx_dicts,
        current_balance=120000.0,
        monthly_income=float(current_user.monthly_income or 75000.0),
        currency=current_user.preferred_currency or "INR"
    )

@router.get("/forecast/evaluation", response_model=ModelEvaluationMetrics)
async def get_forecast_model_evaluation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns holdout evaluation benchmark metrics (MAE, MAPE, RMSE) comparing
    the advanced seasonal/trend model against the simple moving average baseline.
    """
    forecast_data = await get_expense_forecast(current_user=current_user, db=db)
    return forecast_data.get("evaluation") or expense_forecaster.evaluate_forecast_models([])

