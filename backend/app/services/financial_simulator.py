import math
from datetime import date, timedelta
from typing import Dict, Any, List, Optional

class FinancialSimulator:
    """
    Deterministic What-If Financial Simulation Engine.
    Executes decimal-safe calculations for:
    - Monthly cash flow & Net surplus deltas
    - Annual savings impact (12-month & multi-year compounding)
    - Goal completion timeline acceleration
    - Budget utilization & headroom optimization
    - Projected Financial Health Score impact
    - Post-simulation AI explanations (deterministic data only)
    """

    @classmethod
    def run_simulation(
        cls,
        base_income: float = 75000.0,
        base_expenses: float = 35000.0,
        base_balance: float = 120000.0,
        income_change_pct: float = 0.0,
        income_change_abs: float = 0.0,
        food_spend_reduction: float = 0.0,
        shopping_spend_reduction: float = 0.0,
        discretionary_spend_reduction: float = 0.0,
        removed_subscriptions_amount: float = 0.0,
        extra_goal_contribution: float = 0.0,
        one_time_purchase_amount: float = 0.0,
        budget_limit_change: float = 0.0,
        inflation_rate: float = 6.0,
        investment_roi: float = 12.0,
        timeline_months: int = 24,
        active_goals: Optional[List[Dict[str, Any]]] = None,
        currency: str = "INR"
    ) -> Dict[str, Any]:
        """
        Calculates side-by-side Current vs Simulated scenario comparisons deterministically.
        """
        # 1. Baseline Calculations
        curr_monthly_inc = max(base_income, 1000.0)
        curr_monthly_exp = max(base_expenses, 1000.0)
        curr_monthly_net = curr_monthly_inc - curr_monthly_exp
        curr_sav_rate = round((curr_monthly_net / curr_monthly_inc) * 100.0, 1) if curr_monthly_inc > 0 else 0.0
        curr_annual_sav = round(curr_monthly_net * 12.0, 2)
        curr_budget_limit = curr_monthly_exp * 1.15
        curr_budget_util = round((curr_monthly_exp / curr_budget_limit) * 100.0, 1) if curr_budget_limit > 0 else 0.0
        
        # Baseline Health Score
        curr_health = cls._calc_health_score(curr_sav_rate, curr_monthly_inc, curr_monthly_exp, base_balance)

        # 2. Simulated Scenario Calculations
        # Income changes
        pct_inc_boost = curr_monthly_inc * (income_change_pct / 100.0)
        sim_monthly_inc = max(curr_monthly_inc + pct_inc_boost + income_change_abs, 1000.0)

        # Total expense reductions
        total_exp_reduction = (
            food_spend_reduction +
            shopping_spend_reduction +
            discretionary_spend_reduction +
            removed_subscriptions_amount
        )
        sim_monthly_exp = max(curr_monthly_exp - total_exp_reduction, 5000.0)
        sim_monthly_net = sim_monthly_inc - sim_monthly_exp
        sim_sav_rate = round((sim_monthly_net / sim_monthly_inc) * 100.0, 1) if sim_monthly_inc > 0 else 0.0
        sim_annual_sav = round(sim_monthly_net * 12.0, 2)

        # Budget Impact
        sim_budget_limit = max(curr_budget_limit + budget_limit_change, sim_monthly_exp)
        sim_budget_util = round((sim_monthly_exp / sim_budget_limit) * 100.0, 1) if sim_budget_limit > 0 else 0.0

        # Simulated Health Score
        sim_health = cls._calc_health_score(sim_sav_rate, sim_monthly_inc, sim_monthly_exp, base_balance - one_time_purchase_amount)

        # Deltas
        net_monthly_delta = round(sim_monthly_net - curr_monthly_net, 2)
        annual_savings_delta = round(sim_annual_sav - curr_annual_sav, 2)
        health_delta = sim_health["score"] - curr_health["score"]
        budget_util_delta = round(sim_budget_util - curr_budget_util, 1)

        # 3. Goal Completion Impact Calculations
        goal_impacts = []
        sample_goals = active_goals or [
            {"title": "MacBook Pro M-Series", "target_amount": 80000.0, "current_amount": 23000.0, "monthly_saving": 14250.0},
            {"title": "Emergency Safety Reserve", "target_amount": 300000.0, "current_amount": 180000.0, "monthly_saving": 12000.0},
            {"title": "Global Vacation Fund", "target_amount": 150000.0, "current_amount": 75000.0, "monthly_saving": 18750.0}
        ]

        today = date.today()
        for g in sample_goals:
            targ = float(g.get("target_amount", 50000.0))
            curr = float(g.get("current_amount", 0.0))
            rem = max(targ - curr, 0.0)
            base_monthly = max(float(g.get("monthly_saving", 5000.0)), 1000.0)
            
            # Base completion months
            base_months = math.ceil(rem / base_monthly) if base_monthly > 0 else 12
            
            # Boosted monthly allocation from simulation surplus
            boosted_monthly = base_monthly + (extra_goal_contribution * 0.5) + (max(net_monthly_delta, 0.0) * 0.4)
            sim_months = math.ceil(rem / max(boosted_monthly, 1000.0)) if rem > 0 else 0
            months_saved = max(base_months - sim_months, 0)
            
            accel_date = (today + timedelta(days=sim_months * 30.5)).strftime("%B %Y")

            goal_impacts.append({
                "goal_title": g.get("title", "Goal"),
                "target_amount": targ,
                "current_amount": curr,
                "remaining_amount": rem,
                "baseline_months_to_complete": base_months,
                "simulated_months_to_complete": sim_months,
                "months_saved": months_saved,
                "accelerated_completion_date": accel_date
            })

        # 4. Multi-Year Compounding Timeline Simulation
        monthly_inflation = (inflation_rate / 100.0) / 12.0
        monthly_roi = (investment_roi / 100.0) / 12.0
        timeline = []
        cum_portfolio = max(base_balance - one_time_purchase_amount, 0.0)

        for m in range(1, timeline_months + 1):
            adj_expense = sim_monthly_exp * ((1 + monthly_inflation) ** m)
            m_saved = sim_monthly_inc - adj_expense
            cum_portfolio = (cum_portfolio * (1 + monthly_roi)) + m_saved
            timeline.append({
                "month": m,
                "projected_expense": round(adj_expense, 2),
                "net_monthly_saved": round(m_saved, 2),
                "cumulative_portfolio": round(cum_portfolio, 2)
            })

        # 5. Post-Simulation AI Plain Language Explanation
        ai_exp = cls._generate_ai_explanation(
            net_monthly_delta=net_monthly_delta,
            annual_savings_delta=annual_savings_delta,
            health_delta=health_delta,
            sim_sav_rate=sim_sav_rate,
            goal_impacts=goal_impacts,
            currency=currency
        )

        return {
            "current_scenario": {
                "monthly_income": round(curr_monthly_inc, 2),
                "monthly_expenses": round(curr_monthly_exp, 2),
                "monthly_net_cash_flow": round(curr_monthly_net, 2),
                "savings_rate_pct": curr_sav_rate,
                "annual_savings": curr_annual_sav,
                "total_budget_limit": round(curr_budget_limit, 2),
                "budget_utilization_pct": curr_budget_util,
                "health_score": curr_health["score"],
                "health_rating": curr_health["rating"]
            },
            "simulated_scenario": {
                "monthly_income": round(sim_monthly_inc, 2),
                "monthly_expenses": round(sim_monthly_exp, 2),
                "monthly_net_cash_flow": round(sim_monthly_net, 2),
                "savings_rate_pct": sim_sav_rate,
                "annual_savings": sim_annual_sav,
                "total_budget_limit": round(sim_budget_limit, 2),
                "budget_utilization_pct": sim_budget_util,
                "health_score": sim_health["score"],
                "health_rating": sim_health["rating"]
            },
            "net_monthly_delta": net_monthly_delta,
            "annual_savings_delta": annual_savings_delta,
            "health_score_delta": health_delta,
            "budget_utilization_delta_pct": budget_util_delta,
            "goal_impacts": goal_impacts,
            "simulated_timeline": timeline,
            "projected_net_savings": round(cum_portfolio, 2),
            "runway_impact_months": round(cum_portfolio / max(sim_monthly_exp, 1.0), 1),
            "ai_explanation": ai_exp,
            "guru_critique": {
                "buffett": f"By increasing annual surplus by {currency} {annual_savings_delta:,.2f}, disciplined compounding in index assets will multiply your financial runway significantly.",
                "kiyosaki": f"Redirecting your net monthly boost of +{currency} {net_monthly_delta:,.2f} into cash-flowing assets lowers your earned wage dependency.",
                "sethi": f"Automate the extra +{currency} {net_monthly_delta:,.2f} transfer directly into your goal accounts on payday to lock in the wins automatically."
            }
        }

    @classmethod
    def _calc_health_score(cls, savings_rate: float, income: float, expenses: float, balance: float) -> Dict[str, Any]:
        # Deterministic scoring components
        # 1. Savings rate component (0 - 100)
        sav_score = min(max(savings_rate * 2.5, 0.0), 100.0)
        # 2. Emergency coverage component
        months_cov = balance / max(expenses, 1.0)
        em_score = min(max((months_cov / 6.0) * 100.0, 0.0), 100.0)
        # 3. Debt & Burn safety
        burn_score = 85.0 if expenses <= income * 0.70 else 60.0

        total_score = int(round((sav_score * 0.40) + (em_score * 0.35) + (burn_score * 0.25)))
        total_score = max(10, min(total_score, 100))

        if total_score >= 80:
            rating = "Excellent"
        elif total_score >= 65:
            rating = "Good"
        elif total_score >= 50:
            rating = "Fair"
        else:
            rating = "Needs Attention"

        return {"score": total_score, "rating": rating}

    @classmethod
    def _generate_ai_explanation(
        cls,
        net_monthly_delta: float,
        annual_savings_delta: float,
        health_delta: int,
        sim_sav_rate: float,
        goal_impacts: List[Dict[str, Any]],
        currency: str
    ) -> str:
        parts = []
        if net_monthly_delta > 0:
            parts.append(
                f"Your simulated scenario unlocks +{currency} {net_monthly_delta:,.2f}/month in net surplus "
                f"(+{currency} {annual_savings_delta:,.2f} additional annual savings), boosting your overall savings rate to {sim_sav_rate}%."
            )
        elif net_monthly_delta < 0:
            parts.append(
                f"Your simulated scenario reduces net monthly cash flow by {currency} {abs(net_monthly_delta):,.2f}/month."
            )
        else:
            parts.append("Your cash flow remains consistent with your current baseline.")

        if health_delta > 0:
            parts.append(f"Financial Health Score is projected to increase by +{health_delta} points.")
        elif health_delta < 0:
            parts.append(f"Financial Health Score decreases by {abs(health_delta)} points.")

        top_goal = next((g for g in goal_impacts if g["months_saved"] > 0), None)
        if top_goal:
            parts.append(
                f"Your '{top_goal['goal_title']}' goal will be achieved {top_goal['months_saved']} months earlier "
                f"({top_goal['accelerated_completion_date']})."
            )

        return " ".join(parts)

financial_simulator = FinancialSimulator()
