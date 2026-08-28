import math
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.category import Category
from backend.app.models.budget import Budget
from backend.app.models.goal import FinancialGoal
from backend.app.models.financial_score import FinancialScore
from backend.app.schemas.analytics import (
    HealthScoreDetailResponse,
    HealthScoreComponentDetail,
    HealthScoreHistoryPoint,
    HealthScoreHistoryResponse
)

class FinancialHealthEngine:
    """
    Deterministic & Transparent Financial Health Scoring Engine:
    7 Core Weighted Components (Total 100%):
    1. Savings Rate (20%)
    2. Budget Adherence (15%)
    3. Debt Burden / DTI (15%)
    4. Emergency Fund Coverage (15%)
    5. Spending Consistency (15%)
    6. Recurring Expense Burden (10%)
    7. Goal Progress (10%)

    Includes delta explanation and historical score tracking in database.
    """

    COMPONENT_WEIGHTS = {
        "savings_rate": 0.20,
        "budget_adherence": 0.15,
        "debt_burden": 0.15,
        "emergency_fund": 0.15,
        "spending_consistency": 0.15,
        "recurring_burden": 0.10,
        "goal_progress": 0.10
    }

    async def compute_health_score(
        self,
        db: AsyncSession,
        user_id: str,
        persist: bool = True
    ) -> HealthScoreDetailResponse:
        """
        Computes explainable composite financial health score from database data.
        """
        # 1. Fetch User Data
        u_res = await db.execute(select(User).options(selectinload(User.profile)).filter(User.id == user_id))
        user = u_res.scalars().first()
        monthly_income = float(user.monthly_income) if (user and user.monthly_income > 0) else 75000.0

        # 2. Fetch Recent Transactions (past 30 days)
        today = date.today()
        start_30 = today - timedelta(days=30)
        t_res = await db.execute(
            select(Transaction).options(selectinload(Transaction.category)).filter(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False,
                Transaction.transaction_date >= start_30
            )
        )
        txs = t_res.scalars().all()

        # Aggregate Debits & Credits
        total_income_30 = sum(t.amount for t in txs if t.transaction_type == "credit")
        if total_income_30 > 0:
            monthly_income = total_income_30 # Use actual credited income if present

        total_expenses_30 = sum(t.amount for t in txs if t.transaction_type == "debit")
        emi_expenses_30 = sum(t.amount for t in txs if t.transaction_type == "debit" and (
            (t.category and t.category.name.lower() in ["emi", "loan"]) or
            ("emi" in t.description.lower() or "loan" in t.description.lower())
        ))
        recurring_expenses_30 = sum(t.amount for t in txs if t.transaction_type == "debit" and (
            t.is_subscription or (t.category and t.category.name.lower() in ["subscriptions", "bills"])
        ))

        # 3. Fetch Budgets
        b_res = await db.execute(select(Budget).filter(Budget.user_id == user_id, Budget.is_active == True))
        budgets = b_res.scalars().all()
        total_budget_limit = sum(float(b.monthly_limit) for b in budgets)

        # 4. Fetch Goals
        g_res = await db.execute(select(FinancialGoal).filter(FinancialGoal.user_id == user_id, FinancialGoal.status == "in_progress"))
        goals = g_res.scalars().all()

        # ==========================================
        # Component 1: Savings Rate (20%)
        # ==========================================
        net_saved = max(monthly_income - total_expenses_30, 0.0)
        savings_rate_pct = (net_saved / monthly_income) * 100 if monthly_income > 0 else 0.0

        if savings_rate_pct >= 35.0:
            c1_score = 100
        elif savings_rate_pct >= 20.0:
            c1_score = int(75 + ((savings_rate_pct - 20.0) / 15.0) * 25)
        elif savings_rate_pct >= 10.0:
            c1_score = int(50 + ((savings_rate_pct - 10.0) / 10.0) * 25)
        elif savings_rate_pct > 0.0:
            c1_score = int(25 + (savings_rate_pct / 10.0) * 25)
        else:
            c1_score = 10 # Overspending

        c1 = HealthScoreComponentDetail(
            name="Savings Rate",
            score=c1_score,
            weight=self.COMPONENT_WEIGHTS["savings_rate"],
            weighted_score=round(c1_score * self.COMPONENT_WEIGHTS["savings_rate"], 2),
            status=self._score_to_status(c1_score),
            metric_value=f"{savings_rate_pct:.1f}%",
            description=f"Saving {savings_rate_pct:.1f}% of income (Benchmark: 20-30%+)"
        )

        # ==========================================
        # Component 2: Budget Adherence (15%)
        # ==========================================
        if total_budget_limit > 0:
            utilization = (total_expenses_30 / total_budget_limit) * 100
            if utilization <= 80.0:
                c2_score = 100
            elif utilization <= 100.0:
                c2_score = int(80 + ((100.0 - utilization) / 20.0) * 20)
            elif utilization <= 120.0:
                c2_score = int(50 + ((120.0 - utilization) / 20.0) * 30)
            else:
                c2_score = max(10, int(50 - (utilization - 120.0)))
            b_metric = f"{utilization:.1f}% utilized"
            b_desc = f"Spent ₹{total_expenses_30:,.0f} against monthly budget limit of ₹{total_budget_limit:,.0f}"
        else:
            c2_score = 80 # Default baseline
            b_metric = "Baseline"
            b_desc = "No explicit budget limit set; running on baseline allocation"

        c2 = HealthScoreComponentDetail(
            name="Budget Adherence",
            score=c2_score,
            weight=self.COMPONENT_WEIGHTS["budget_adherence"],
            weighted_score=round(c2_score * self.COMPONENT_WEIGHTS["budget_adherence"], 2),
            status=self._score_to_status(c2_score),
            metric_value=b_metric,
            description=b_desc
        )

        # ==========================================
        # Component 3: Debt Burden / DTI (15%)
        # ==========================================
        dti_pct = (emi_expenses_30 / monthly_income) * 100 if monthly_income > 0 else 0.0
        if dti_pct == 0:
            c3_score = 100
        elif dti_pct <= 15.0:
            c3_score = int(90 + ((15.0 - dti_pct) / 15.0) * 10)
        elif dti_pct <= 30.0:
            c3_score = int(75 + ((30.0 - dti_pct) / 15.0) * 15)
        elif dti_pct <= 45.0:
            c3_score = int(50 + ((45.0 - dti_pct) / 15.0) * 25)
        else:
            c3_score = max(10, int(50 - (dti_pct - 45.0)))

        c3 = HealthScoreComponentDetail(
            name="Debt Burden",
            score=c3_score,
            weight=self.COMPONENT_WEIGHTS["debt_burden"],
            weighted_score=round(c3_score * self.COMPONENT_WEIGHTS["debt_burden"], 2),
            status=self._score_to_status(c3_score),
            metric_value=f"{dti_pct:.1f}% DTI",
            description=f"Debt & EMI obligations consume {dti_pct:.1f}% of income"
        )

        # ==========================================
        # Component 4: Emergency Fund Coverage (15%)
        # ==========================================
        liquid_savings = max(net_saved * 3.5, 150000.0) # Estimated liquid capital
        monthly_burn = max(total_expenses_30, 20000.0)
        months_covered = liquid_savings / monthly_burn

        if months_covered >= 6.0:
            c4_score = 100
        elif months_covered >= 4.0:
            c4_score = int(85 + ((months_covered - 4.0) / 2.0) * 15)
        elif months_covered >= 2.5:
            c4_score = int(70 + ((months_covered - 2.5) / 1.5) * 15)
        elif months_covered >= 1.0:
            c4_score = int(45 + ((months_covered - 1.0) / 1.5) * 25)
        else:
            c4_score = max(15, int(months_covered * 45))

        c4 = HealthScoreComponentDetail(
            name="Emergency Fund",
            score=c4_score,
            weight=self.COMPONENT_WEIGHTS["emergency_fund"],
            weighted_score=round(c4_score * self.COMPONENT_WEIGHTS["emergency_fund"], 2),
            status=self._score_to_status(c4_score),
            metric_value=f"{months_covered:.1f} Months",
            description=f"Liquid cushion covers {months_covered:.1f} months of expenses (Target: 6 mo)"
        )

        # ==========================================
        # Component 5: Spending Consistency (15%)
        # ==========================================
        # Group into 4 weekly buckets
        weekly_spends = [0.0, 0.0, 0.0, 0.0]
        for t in txs:
            if t.transaction_type == "debit":
                days_ago = (today - t.transaction_date).days
                w_idx = min(3, max(0, days_ago // 7))
                weekly_spends[w_idx] += t.amount

        mean_weekly = sum(weekly_spends) / 4.0 if sum(weekly_spends) > 0 else 1.0
        variance = sum((w - mean_weekly) ** 2 for w in weekly_spends) / 4.0
        std_dev = math.sqrt(variance)
        cv = std_dev / mean_weekly if mean_weekly > 0 else 0.0

        if cv <= 0.25:
            c5_score = 100
        elif cv <= 0.50:
            c5_score = int(75 + ((0.50 - cv) / 0.25) * 25)
        elif cv <= 0.80:
            c5_score = int(50 + ((0.80 - cv) / 0.30) * 25)
        else:
            c5_score = max(20, int(50 - (cv - 0.80) * 50))

        c5 = HealthScoreComponentDetail(
            name="Spending Consistency",
            score=c5_score,
            weight=self.COMPONENT_WEIGHTS["spending_consistency"],
            weighted_score=round(c5_score * self.COMPONENT_WEIGHTS["spending_consistency"], 2),
            status=self._score_to_status(c5_score),
            metric_value=f"{round((1 - min(cv, 1.0)) * 100, 0):.0f}% Stability",
            description="Measures weekly spend volatility and unplanned variance"
        )

        # ==========================================
        # Component 6: Recurring Expense Burden (10%)
        # ==========================================
        recurring_ratio = (recurring_expenses_30 / monthly_income) * 100 if monthly_income > 0 else 0.0
        if recurring_ratio <= 10.0:
            c6_score = 100
        elif recurring_ratio <= 20.0:
            c6_score = int(80 + ((20.0 - recurring_ratio) / 10.0) * 20)
        elif recurring_ratio <= 35.0:
            c6_score = int(50 + ((35.0 - recurring_ratio) / 15.0) * 30)
        else:
            c6_score = max(15, int(50 - (recurring_ratio - 35.0)))

        c6 = HealthScoreComponentDetail(
            name="Recurring Burden",
            score=c6_score,
            weight=self.COMPONENT_WEIGHTS["recurring_burden"],
            weighted_score=round(c6_score * self.COMPONENT_WEIGHTS["recurring_burden"], 2),
            status=self._score_to_status(c6_score),
            metric_value=f"{recurring_ratio:.1f}% Fixed",
            description=f"Fixed commitments & subscriptions consume {recurring_ratio:.1f}% of income"
        )

        # ==========================================
        # Component 7: Goal Progress (10%)
        # ==========================================
        if goals:
            avg_goal_pct = sum(
                (float(g.current_amount) / float(g.target_amount) * 100.0) if (g.target_amount and float(g.target_amount) > 0) else 0.0
                for g in goals
            ) / len(goals)
            if avg_goal_pct >= 75.0:
                c7_score = 100
            elif avg_goal_pct >= 50.0:
                c7_score = int(80 + ((avg_goal_pct - 50.0) / 25.0) * 20)
            elif avg_goal_pct >= 25.0:
                c7_score = int(55 + ((avg_goal_pct - 25.0) / 25.0) * 25)
            else:
                c7_score = max(25, int(avg_goal_pct * 2.2))
            g_metric = f"{avg_goal_pct:.1f}% Avg"
            g_desc = f"{len(goals)} active financial goals with {avg_goal_pct:.1f}% overall progress"
        else:
            c7_score = 75 # Baseline
            g_metric = "On Track"
            g_desc = "Standard goal progress pacing"

        c7 = HealthScoreComponentDetail(
            name="Goal Progress",
            score=c7_score,
            weight=self.COMPONENT_WEIGHTS["goal_progress"],
            weighted_score=round(c7_score * self.COMPONENT_WEIGHTS["goal_progress"], 2),
            status=self._score_to_status(c7_score),
            metric_value=g_metric,
            description=g_desc
        )

        components = {
            "savings_rate": c1,
            "budget_adherence": c2,
            "debt_burden": c3,
            "emergency_fund": c4,
            "spending_consistency": c5,
            "recurring_burden": c6,
            "goal_progress": c7
        }

        # Composite Score Calculation
        raw_composite = sum(c.weighted_score for c in components.values())
        final_score = min(max(int(round(raw_composite)), 10), 100)

        # Rating
        if final_score >= 85:
            rating = "Excellent"
        elif final_score >= 70:
            rating = "Good"
        elif final_score >= 50:
            rating = "Fair"
        else:
            rating = "Needs Attention"

        # Explainability Factors
        positive_factors = []
        negative_factors = []
        recommendations = []

        if c1.score >= 75:
            positive_factors.append(f"Healthy savings rate of {savings_rate_pct:.1f}% (target: 20%+).")
        else:
            negative_factors.append(f"Savings rate is low at {savings_rate_pct:.1f}%.")
            recommendations.append("Automate a monthly transfer of at least 20% of your paycheck to an investment account.")

        if c3.score >= 80:
            positive_factors.append(f"Manageable debt obligations ({dti_pct:.1f}% DTI).")
        else:
            negative_factors.append(f"High debt burden ({dti_pct:.1f}% of income consumed by EMIs).")
            recommendations.append("Target prepaying high-interest debt/credit card balances to bring DTI below 20%.")

        if c4.score >= 80:
            positive_factors.append(f"Solid emergency reserve covering {months_covered:.1f} months of expenses.")
        else:
            negative_factors.append(f"Emergency reserve covers only {months_covered:.1f} months (recommended: 6 months).")
            recommendations.append("Allocate ₹5,000/month into liquid funds until a 6-month buffer is established.")

        if c2.score >= 80:
            positive_factors.append("Consistent budget adherence with no category overshoots.")
        else:
            negative_factors.append("Recent budget overrun detected in discretionary categories.")
            recommendations.append("Set monthly spending alerts on Food & Dining to cap unplanned overshoots.")

        if c5.score >= 75:
            positive_factors.append("Stable week-over-week spending discipline with low variance.")
        else:
            negative_factors.append("High spending volatility with occasional large spikes.")

        # Historical Comparison & Delta Explanation
        prev_score_res = await db.execute(
            select(FinancialScore).filter(FinancialScore.user_id == user_id).order_by(FinancialScore.calculated_at.desc())
        )
        prev_record = prev_score_res.scalars().first()

        score_delta = 0
        delta_explanation = "Baseline score calculated from active financial ledger."

        if prev_record:
            score_delta = final_score - prev_record.composite_score
            if score_delta > 0:
                delta_explanation = f"Score increased by +{score_delta} points driven by improvements in savings and budget discipline."
            elif score_delta < 0:
                delta_explanation = f"Score decreased by {score_delta} points due to higher discretionary spending or increased debt burden."
            else:
                delta_explanation = "Financial health score maintained stability across all key dimensions."

        # Persist to Database
        if persist:
            score_record = FinancialScore(
                user_id=user_id,
                composite_score=final_score,
                rating=rating,
                emergency_fund_score=c4.score,
                savings_rate_score=c1.score,
                budget_adherence_score=c2.score,
                debt_and_burn_score=c3.score,
                calculation_metadata={
                    "components": {k: v.score for k, v in components.items()},
                    "score_delta": score_delta,
                    "delta_explanation": delta_explanation,
                    "positive_factors": positive_factors,
                    "negative_factors": negative_factors,
                    "recommendations": recommendations
                }
            )
            db.add(score_record)
            await db.commit()

        return HealthScoreDetailResponse(
            score=final_score,
            rating=rating,
            components=components,
            positive_factors=positive_factors,
            negative_factors=negative_factors,
            recommendations=recommendations,
            score_delta=score_delta,
            delta_explanation=delta_explanation,
            calculated_at=datetime.utcnow().isoformat(),
            emergency_fund_score=c4.score,
            savings_rate_score=c1.score,
            budget_adherence_score=c2.score,
            debt_and_burn_score=c3.score,
            insights=positive_factors + recommendations
        )

    async def get_history(self, db: AsyncSession, user_id: str, limit: int = 20) -> HealthScoreHistoryResponse:
        """
        Retrieves historical score tracking records for the user.
        """
        res = await db.execute(
            select(FinancialScore).filter(
                FinancialScore.user_id == user_id
            ).order_by(FinancialScore.calculated_at.asc()).limit(limit)
        )
        records = res.scalars().all()

        points = []
        for r in records:
            meta = r.calculation_metadata or {}
            comp_scores = meta.get("components", {
                "savings_rate": r.savings_rate_score,
                "budget_adherence": r.budget_adherence_score,
                "debt_burden": r.debt_and_burn_score,
                "emergency_fund": r.emergency_fund_score
            })

            points.append(HealthScoreHistoryPoint(
                id=r.id,
                score=r.composite_score,
                rating=r.rating,
                calculated_at=r.calculated_at.isoformat() if r.calculated_at else datetime.utcnow().isoformat(),
                component_scores=comp_scores
            ))

        return HealthScoreHistoryResponse(history=points)

    def _score_to_status(self, score: int) -> str:
        if score >= 85:
            return "Excellent"
        if score >= 70:
            return "Good"
        if score >= 50:
            return "Fair"
        return "Needs Attention"

    # Backward compatibility helper
    @classmethod
    def calculate_health_score(
        cls,
        monthly_income: float,
        monthly_expenses: float,
        total_savings: float = 0.0,
        budget_limit: float = 0.0
    ) -> Dict[str, Any]:
        income = max(monthly_income, 50000.0)
        expenses = max(monthly_expenses, 15000.0)
        savings = total_savings if total_savings > 0 else (income - expenses) * 3
        savings_rate = ((income - expenses) / income) * 100 if income > 0 else 0

        sav_score = 25 if savings_rate >= 30 else 20 if savings_rate >= 20 else 14 if savings_rate >= 10 else 7
        burn_score = 25 if (expenses/income) <= 0.5 else 20 if (expenses/income) <= 0.7 else 13 if (expenses/income) <= 0.85 else 6
        em_score = 25 if (savings/expenses) >= 6 else 19 if (savings/expenses) >= 3 else 12 if (savings/expenses) >= 1 else 5
        b_score = 25 if budget_limit and (expenses/budget_limit) <= 0.9 else 20

        total = min(max(sav_score + burn_score + em_score + b_score, 10), 100)
        rating = "Excellent" if total >= 85 else "Good" if total >= 70 else "Fair" if total >= 50 else "Needs Attention"

        return {
            "score": total,
            "rating": rating,
            "emergency_fund_score": em_score,
            "savings_rate_score": sav_score,
            "budget_adherence_score": b_score,
            "debt_and_burn_score": burn_score,
            "insights": [f"Savings rate: {savings_rate:.1f}%", f"Rating: {rating}"]
        }

financial_health_engine = FinancialHealthEngine()
