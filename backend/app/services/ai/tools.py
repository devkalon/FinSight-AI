import math
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.models.transaction import Transaction
from backend.app.models.category import Category
from backend.app.models.budget import Budget
from backend.app.models.goal import FinancialGoal
from backend.app.models.subscription import Subscription
from backend.app.services.financial_analytics import financial_analytics_engine
from backend.app.services.financial_health import financial_health_engine
from backend.app.services.ai.rag_engine import rag_engine

class FinancialTools:
    """
    Controlled, authorized, deterministic financial tools for AI Agent execution.
    Never allows LLMs to query database directly or hallucinate numbers.
    All data is strictly scoped to authenticated user_id.
    """

    # 1. Get Transactions
    @classmethod
    async def get_transactions(
        cls,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_name: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        query = select(Transaction).options(selectinload(Transaction.category)).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False
        )
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        if category_name:
            query = query.join(Transaction.category).filter(Category.name.ilike(f"%{category_name}%"))

        query = query.order_by(Transaction.transaction_date.desc()).limit(limit)
        res = await db.execute(query)
        txs = res.scalars().all()

        if not txs:
            return {
                "count": 0,
                "items": [],
                "message": "No transactions found matching the specified timeframe or category filter."
            }

        return {
            "count": len(txs),
            "items": [
                {
                    "date": t.transaction_date.isoformat(),
                    "description": t.description,
                    "amount": float(t.amount),
                    "type": t.transaction_type,
                    "category": t.category.name if t.category else "Uncategorized",
                    "merchant": t.merchant_name
                }
                for t in txs
            ]
        }

    # 2. Get Income
    @classmethod
    async def get_income(
        cls,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        summary = await financial_analytics_engine.calculate_summary(
            db=db, user_id=user_id, start_date=start_date, end_date=end_date
        )
        return {
            "total_income": summary.total_income,
            "period": f"{summary.start_date} to {summary.end_date}",
            "transaction_count": summary.transaction_count,
            "currency": summary.currency
        }

    # 3. Get Expenses
    @classmethod
    async def get_expenses(
        cls,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        summary = await financial_analytics_engine.calculate_summary(
            db=db, user_id=user_id, start_date=start_date, end_date=end_date
        )
        return {
            "total_expenses": summary.total_expenses,
            "net_savings": summary.net_savings,
            "average_daily_spending": summary.average_daily_spending,
            "period": f"{summary.start_date} to {summary.end_date}",
            "currency": summary.currency
        }

    # 4. Get Category Spending
    @classmethod
    async def get_category_spending(
        cls,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        categories = await financial_analytics_engine.calculate_category_spending(
            db=db, user_id=user_id, start_date=start_date, end_date=end_date
        )
        if not categories:
            return {"categories": [], "message": "No expense category records found for this period."}

        return {
            "categories": [
                {
                    "category": c.category_name,
                    "group_type": c.group_type,
                    "amount": c.total_amount,
                    "percentage": c.percentage_of_total,
                    "count": c.transaction_count
                }
                for c in categories
            ]
        }

    # 5. Get Budget Status
    @classmethod
    async def get_budget_status(
        cls,
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        items = await financial_analytics_engine.calculate_budget_utilization(db=db, user_id=user_id)
        if not items:
            return {"budgets": [], "message": "No active monthly category budgets configured."}

        over_budget = [b for b in items if b.is_over_budget]
        return {
            "total_budgeted_categories": len(items),
            "over_budget_count": len(over_budget),
            "budgets": [
                {
                    "category": b.category_name,
                    "limit": b.budgeted_amount,
                    "spent": b.spent_amount,
                    "utilization_pct": b.utilization_pct,
                    "remaining": b.remaining_amount,
                    "is_over_budget": b.is_over_budget
                }
                for b in items
            ]
        }

    # 6. Get Goals
    @classmethod
    async def get_goals(
        cls,
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        res = await db.execute(
            select(FinancialGoal).filter(
                FinancialGoal.user_id == user_id,
                FinancialGoal.is_deleted == False
            ).order_by(FinancialGoal.target_date.asc())
        )
        goals = res.scalars().all()
        if not goals:
            return {"goals": [], "message": "No financial goals currently created."}

        return {
            "goal_count": len(goals),
            "goals": [
                {
                    "title": g.title,
                    "category": g.category,
                    "target_amount": float(g.target_amount),
                    "current_amount": float(g.current_amount),
                    "progress_percentage": round((float(g.current_amount) / float(g.target_amount) * 100) if float(g.target_amount) > 0 else 0, 1),
                    "target_date": g.target_date.isoformat(),
                    "status": g.status
                }
                for g in goals
            ]
        }

    # 7. Calculate Savings Rate
    @classmethod
    async def calculate_savings_rate(
        cls,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        summary = await financial_analytics_engine.calculate_summary(
            db=db, user_id=user_id, start_date=start_date, end_date=end_date
        )
        return {
            "savings_rate_pct": summary.savings_rate_pct,
            "total_income": summary.total_income,
            "total_expenses": summary.total_expenses,
            "net_savings": summary.net_savings,
            "benchmark_evaluation": "Optimal (>20%)" if summary.savings_rate_pct >= 20.0 else "Needs Improvement (<20%)"
        }

    # 8. Calculate Financial Health Score
    @classmethod
    async def calculate_financial_health(
        cls,
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        score_res = await financial_health_engine.compute_health_score(db=db, user_id=user_id, persist=False)
        return {
            "composite_score": score_res.score,
            "rating": score_res.rating,
            "component_scores": {k: v.score for k, v in score_res.components.items()},
            "positive_factors": score_res.positive_factors,
            "negative_factors": score_res.negative_factors,
            "recommendations": score_res.recommendations,
            "delta_explanation": score_res.delta_explanation
        }

    # 9. Detect Anomalies
    @classmethod
    async def detect_anomalies(
        cls,
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        today = date.today()
        start_60 = today - timedelta(days=60)
        res = await db.execute(
            select(Transaction).options(selectinload(Transaction.category)).filter(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
                Transaction.transaction_date >= start_60
            )
        )
        txs = res.scalars().all()
        debits = [t for t in txs if t.transaction_type == "debit"]
        if not debits:
            return {"anomalies": [], "message": "No recent debit activity found to analyze."}

        avg_debit = sum(t.amount for t in debits) / len(debits)
        threshold = max(avg_debit * 2.5, 5000.0)

        anomalies = [
            {
                "date": t.transaction_date.isoformat(),
                "description": t.description,
                "amount": float(t.amount),
                "category": t.category.name if t.category else "Uncategorized",
                "reason": f"Spike transaction: {float(t.amount)/avg_debit:.1f}x higher than average spend (₹{avg_debit:,.0f})"
            }
            for t in debits if float(t.amount) >= threshold
        ]

        return {
            "average_transaction": round(avg_debit, 2),
            "anomaly_count": len(anomalies),
            "anomalies": anomalies
        }

    # 10. Forecast Expenses
    @classmethod
    async def forecast_expenses(
        cls,
        db: AsyncSession,
        user_id: str,
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        today = date.today()
        start_60 = today - timedelta(days=60)
        res = await db.execute(
            select(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
                Transaction.transaction_date >= start_60,
                Transaction.transaction_type == "debit"
            )
        )
        txs = res.scalars().all()
        total_exp = sum(t.amount for t in txs)
        daily_avg = total_exp / 60.0 if total_exp > 0 else 1200.0
        projected = daily_avg * days_ahead

        return {
            "days_ahead": days_ahead,
            "historical_daily_average": round(daily_avg, 2),
            "projected_expense_total": round(projected, 2),
            "confidence_interval": {
                "lower_bound": round(projected * 0.90, 2),
                "upper_bound": round(projected * 1.15, 2)
            }
        }

    # 11. Get Recurring Expenses
    @classmethod
    async def get_recurring_expenses(
        cls,
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        res = await db.execute(
            select(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.is_active == True
            )
        )
        subs = res.scalars().all()
        total_monthly_recurring = sum(float(s.amount) for s in subs)

        return {
            "recurring_count": len(subs),
            "total_monthly_recurring": total_monthly_recurring,
            "subscriptions": [
                {
                    "service_name": s.service_name,
                    "amount": float(s.amount),
                    "billing_cycle": s.billing_cycle,
                    "next_billing_date": s.next_billing_date.isoformat() if s.next_billing_date else None
                }
                for s in subs
            ]
        }

    # 12. Search Financial Knowledge (RAG)
    @classmethod
    async def search_financial_knowledge(
        cls,
        db: Optional[AsyncSession] = None,
        user_id: Optional[str] = None,
        query: str = "",
        top_k: int = 3,
        relevance_threshold: float = 0.20
    ) -> Dict[str, Any]:
        res = await rag_engine.retrieve_user_knowledge(
            db=db,
            user_id=user_id,
            query=query,
            top_k=top_k,
            relevance_threshold=relevance_threshold
        )
        return {
            "query": query,
            "results_count": res["results_count"],
            "knowledge_items": res["chunks"],
            "answer_supported": res["answer_supported"],
            "message": res["message"]
        }

    # ==========================================
    # Deterministic Calculators
    # ==========================================
    @classmethod
    def calculate_sip(cls, monthly_investment: float, annual_rate_pct: float = 12.0, years: int = 10) -> Dict[str, Any]:
        i = (annual_rate_pct / 100) / 12
        n = years * 12
        total_invested = monthly_investment * n
        future_value = monthly_investment * (((1 + i)**n - 1) / i) * (1 + i)
        wealth_gain = future_value - total_invested
        return {
            "monthly_investment": round(monthly_investment, 2),
            "annual_rate_pct": annual_rate_pct,
            "years": years,
            "total_invested": round(total_invested, 2),
            "estimated_returns": round(wealth_gain, 2),
            "total_maturity_value": round(future_value, 2)
        }

    @classmethod
    def calculate_emi(cls, principal: float, annual_interest_rate: float, tenure_years: int) -> Dict[str, Any]:
        r = (annual_interest_rate / 100) / 12
        n = tenure_years * 12
        emi = (principal * r * (1 + r)**n) / ((1 + r)**n - 1)
        total_repayment = emi * n
        total_interest = total_repayment - principal
        return {
            "principal": round(principal, 2),
            "annual_interest_rate": annual_interest_rate,
            "tenure_years": tenure_years,
            "monthly_emi": round(emi, 2),
            "total_interest_payable": round(total_interest, 2),
            "total_repayment": round(total_repayment, 2)
        }

    @classmethod
    def calculate_emergency_fund_target(cls, monthly_expenses: float, target_months: int = 6) -> Dict[str, Any]:
        recommended_corpus = monthly_expenses * target_months
        return {
            "monthly_living_expenses": round(monthly_expenses, 2),
            "recommended_months": target_months,
            "ideal_emergency_fund": round(recommended_corpus, 2),
            "recommended_instruments": ["High-yield Savings Account (40%)", "Liquid Mutual Funds (40%)", "Sweep-in Fixed Deposit (20%)"]
        }

    @classmethod
    def evaluate_tax_saving_options(cls, taxable_income: float) -> Dict[str, Any]:
        return {
            "taxable_income": taxable_income,
            "recommended_instruments": [
                {"name": "Section 80C (ELSS / PPF)", "max_limit": 150000.0, "lock_in": "3 years (ELSS)"},
                {"name": "Section 80CCD(1B) (NPS Tier-1)", "max_limit": 50000.0, "benefit": "Extra ₹50k deduction"},
                {"name": "Section 80D (Health Insurance)", "max_limit": 25000.0, "benefit": "Medical premium exemption"}
            ],
            "advice": "Under the New Tax Regime, standard tax rates are lower, but if deductions exceed ₹3.75L, the Old Regime may yield greater tax savings."
        }

financial_tools = FinancialTools()
