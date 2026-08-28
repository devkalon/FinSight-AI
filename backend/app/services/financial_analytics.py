import math
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import selectinload

from backend.app.models.transaction import Transaction
from backend.app.models.category import Category
from backend.app.models.budget import Budget, BudgetCategory
from backend.app.schemas.analytics import (
    FinancialSummary,
    MonthOverMonthChange,
    CategorySpending,
    SpendingSplit,
    TopMerchantSpending,
    BudgetUtilizationItem,
    CashFlowPoint,
    SubscriptionItem,
    ComprehensiveAnalyticsDashboard
)

class FinancialAnalyticsEngine:
    """
    Deterministic Financial Analytics Engine for FinSight AI:
    - Decimal-safe money arithmetic
    - Multi-dimensional financial KPI calculations
    - Date-range filtering & Month-over-Month deltas
    - Essential vs Discretionary classification
    - Budget utilization & Category allocations
    """

    @staticmethod
    def _to_decimal(val: Any) -> Decimal:
        if val is None:
            return Decimal("0.00")
        if isinstance(val, Decimal):
            return val
        return Decimal(str(val))

    @staticmethod
    def _to_float(val: Decimal) -> float:
        return float(val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    async def calculate_summary(
        self,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        currency: str = "INR"
    ) -> FinancialSummary:
        """
        Calculates total income, total expenses, net savings, savings rate, and average daily spend.
        """
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date.replace(day=1) # Default to start of current month

        days_in_period = max(1, (end_date - start_date).days + 1)

        # Query all active transactions in window
        query = select(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        )
        res = await db.execute(query)
        txs = res.scalars().all()

        income_dec = Decimal("0.00")
        expense_dec = Decimal("0.00")
        tx_count = len(txs)

        for t in txs:
            amt = self._to_decimal(t.amount)
            if t.transaction_type == "credit":
                income_dec += amt
            elif t.transaction_type == "debit":
                expense_dec += amt

        net_savings_dec = income_dec - expense_dec
        
        if income_dec > Decimal("0.00"):
            savings_rate = (net_savings_dec / income_dec) * Decimal("100.00")
        else:
            savings_rate = Decimal("0.00")

        daily_spend_dec = expense_dec / Decimal(str(days_in_period))

        return FinancialSummary(
            total_income=self._to_float(income_dec),
            total_expenses=self._to_float(expense_dec),
            net_savings=self._to_float(net_savings_dec),
            savings_rate_pct=round(self._to_float(savings_rate), 2),
            average_daily_spending=self._to_float(daily_spend_dec),
            days_in_period=days_in_period,
            transaction_count=tx_count,
            start_date=start_date,
            end_date=end_date,
            currency=currency
        )

    async def calculate_month_over_month(
        self,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> MonthOverMonthChange:
        """
        Computes Month-over-Month percentage & absolute shifts against identical prior period.
        """
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date.replace(day=1)

        period_length = (end_date - start_date).days + 1
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date - timedelta(days=period_length - 1)

        curr_summary = await self.calculate_summary(db, user_id, start_date, end_date)
        prev_summary = await self.calculate_summary(db, user_id, prev_start_date, prev_end_date)

        curr_inc = self._to_decimal(curr_summary.total_income)
        curr_exp = self._to_decimal(curr_summary.total_expenses)
        curr_sav = self._to_decimal(curr_summary.net_savings)

        prev_inc = self._to_decimal(prev_summary.total_income)
        prev_exp = self._to_decimal(prev_summary.total_expenses)
        prev_sav = self._to_decimal(prev_summary.net_savings)

        inc_abs = curr_inc - prev_inc
        exp_abs = curr_exp - prev_exp
        sav_abs = curr_sav - prev_sav

        inc_pct = ((inc_abs / prev_inc) * Decimal("100.00")) if prev_inc > 0 else Decimal("0.00")
        exp_pct = ((exp_abs / prev_exp) * Decimal("100.00")) if prev_exp > 0 else Decimal("0.00")
        sav_pct = ((sav_abs / prev_sav.abs()) * Decimal("100.00")) if prev_sav != 0 else Decimal("0.00")

        return MonthOverMonthChange(
            income_change_pct=round(self._to_float(inc_pct), 2),
            expense_change_pct=round(self._to_float(exp_pct), 2),
            savings_change_pct=round(self._to_float(sav_pct), 2),
            income_change_abs=self._to_float(inc_abs),
            expense_change_abs=self._to_float(exp_abs),
            savings_change_abs=self._to_float(sav_abs),
            prev_period_income=self._to_float(prev_inc),
            prev_period_expense=self._to_float(prev_exp),
            prev_period_savings=self._to_float(prev_sav)
        )

    async def calculate_category_spending(
        self,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CategorySpending]:
        """
        Calculates spending grouped by category with percentages and transaction counts.
        """
        query = select(Transaction).options(selectinload(Transaction.category)).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.transaction_type == "debit"
        )
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        res = await db.execute(query)
        txs = res.scalars().all()

        if not txs:
            return []

        cat_map: Dict[str, Dict[str, Any]] = {}
        total_exp_dec = Decimal("0.00")

        for t in txs:
            amt = self._to_decimal(t.amount)
            total_exp_dec += amt

            cat_name = t.category.name if t.category else "Other"
            cat_id = t.category_id
            group_type = t.category.group_type if t.category else "Want"
            color = t.category.color if (t.category and t.category.color) else "#6366F1"

            if cat_name not in cat_map:
                cat_map[cat_name] = {
                    "category_id": cat_id,
                    "category_name": cat_name,
                    "group_type": group_type,
                    "total_amount_dec": Decimal("0.00"),
                    "transaction_count": 0,
                    "color": color
                }
            cat_map[cat_name]["total_amount_dec"] += amt
            cat_map[cat_name]["transaction_count"] += 1

        results = []
        for name, data in cat_map.items():
            amt_dec = data["total_amount_dec"]
            pct = ((amt_dec / total_exp_dec) * Decimal("100.00")) if total_exp_dec > 0 else Decimal("0.00")
            results.append(CategorySpending(
                category_id=data["category_id"],
                category_name=name,
                group_type=data["group_type"],
                total_amount=self._to_float(amt_dec),
                percentage_of_total=round(self._to_float(pct), 2),
                transaction_count=data["transaction_count"],
                color=data["color"]
            ))

        return sorted(results, key=lambda x: x.total_amount, reverse=True)

    async def calculate_spending_split(
        self,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> SpendingSplit:
        """
        Calculates Essential (Needs) vs Discretionary (Wants) vs Savings/Investment split.
        """
        cat_spending = await self.calculate_category_spending(db, user_id, start_date, end_date)
        
        essential_dec = Decimal("0.00")
        discretionary_dec = Decimal("0.00")
        investment_dec = Decimal("0.00")
        total_dec = Decimal("0.00")

        # Standard classification mapping
        essential_categories = {"food", "bills", "rent", "emi", "healthcare", "insurance", "groceries", "utilities & bills", "utilities"}
        investment_categories = {"investment", "investment & savings", "savings", "mutual funds"}

        for item in cat_spending:
            amt = self._to_decimal(item.total_amount)
            total_dec += amt
            cat_lower = item.category_name.lower()
            group_lower = item.group_type.lower()

            if group_lower == "need" or cat_lower in essential_categories:
                essential_dec += amt
            elif group_lower in ["investment", "savings"] or cat_lower in investment_categories:
                investment_dec += amt
            else:
                discretionary_dec += amt

        if total_dec > Decimal("0.00"):
            ess_pct = (essential_dec / total_dec) * Decimal("100.00")
            disc_pct = (discretionary_dec / total_dec) * Decimal("100.00")
            inv_pct = (investment_dec / total_dec) * Decimal("100.00")
        else:
            ess_pct = disc_pct = inv_pct = Decimal("0.00")

        return SpendingSplit(
            essential_amount=self._to_float(essential_dec),
            essential_pct=round(self._to_float(ess_pct), 2),
            discretionary_amount=self._to_float(discretionary_dec),
            discretionary_pct=round(self._to_float(disc_pct), 2),
            savings_investment_amount=self._to_float(investment_dec),
            savings_investment_pct=round(self._to_float(inv_pct), 2)
        )

    async def calculate_top_merchants(
        self,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 5
    ) -> List[TopMerchantSpending]:
        """
        Calculates largest merchants by spending volume.
        """
        query = select(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.transaction_type == "debit"
        )
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        res = await db.execute(query)
        txs = res.scalars().all()

        if not txs:
            return []

        merchant_map: Dict[str, Dict[str, Any]] = {}
        total_exp_dec = Decimal("0.00")

        for t in txs:
            amt = self._to_decimal(t.amount)
            total_exp_dec += amt
            m_name = (t.merchant_name or t.description or "Unknown Merchant").strip()

            if m_name not in merchant_map:
                merchant_map[m_name] = {"total_amount_dec": Decimal("0.00"), "count": 0}
            merchant_map[m_name]["total_amount_dec"] += amt
            merchant_map[m_name]["count"] += 1

        results = []
        for name, data in merchant_map.items():
            amt_dec = data["total_amount_dec"]
            pct = ((amt_dec / total_exp_dec) * Decimal("100.00")) if total_exp_dec > 0 else Decimal("0.00")
            results.append(TopMerchantSpending(
                merchant_name=name,
                total_amount=self._to_float(amt_dec),
                transaction_count=data["count"],
                percentage_of_expenses=round(self._to_float(pct), 2)
            ))

        results.sort(key=lambda x: x.total_amount, reverse=True)
        return results[:limit]

    async def calculate_budget_utilization(
        self,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[BudgetUtilizationItem]:
        """
        Calculates actual spending vs monthly budget limits per category.
        """
        b_res = await db.execute(
            select(Budget).options(selectinload(Budget.category)).filter(
                Budget.user_id == user_id,
                Budget.is_active == True
            )
        )
        budgets = b_res.scalars().all()

        cat_spending = await self.calculate_category_spending(db, user_id, start_date, end_date)
        spend_by_cat_id = {c.category_id: self._to_decimal(c.total_amount) for c in cat_spending if c.category_id}
        spend_by_cat_name = {c.category_name.lower(): self._to_decimal(c.total_amount) for c in cat_spending}

        results = []
        for b in budgets:
            limit_dec = self._to_decimal(b.monthly_limit)
            cat_id = b.category_id
            cat_name = b.category.name if b.category else "General Budget"
            color = b.category.color if (b.category and b.category.color) else "#6366F1"

            spent_dec = spend_by_cat_id.get(cat_id) or spend_by_cat_name.get(cat_name.lower()) or Decimal("0.00")
            util_pct = ((spent_dec / limit_dec) * Decimal("100.00")) if limit_dec > 0 else Decimal("0.00")
            remaining_dec = limit_dec - spent_dec

            results.append(BudgetUtilizationItem(
                category_id=cat_id,
                category_name=cat_name,
                budgeted_amount=self._to_float(limit_dec),
                spent_amount=self._to_float(spent_dec),
                utilization_pct=round(self._to_float(util_pct), 2),
                remaining_amount=self._to_float(remaining_dec),
                is_over_budget=spent_dec > limit_dec,
                color=color
            ))

        return sorted(results, key=lambda x: x.spent_amount, reverse=True)

    async def calculate_trends(
        self,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CashFlowPoint]:
        """
        Calculates monthly cash flow trends with income, expense, and savings rate.
        """
        query = select(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False
        )
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        res = await db.execute(query)
        txs = res.scalars().all()

        month_map: Dict[str, Dict[str, Decimal]] = {}
        for t in txs:
            m_key = t.transaction_date.strftime("%b %Y")
            if m_key not in month_map:
                month_map[m_key] = {"income": Decimal("0.00"), "expense": Decimal("0.00")}
            
            amt = self._to_decimal(t.amount)
            if t.transaction_type == "credit":
                month_map[m_key]["income"] += amt
            elif t.transaction_type == "debit":
                month_map[m_key]["expense"] += amt

        trends = []
        for m_key, data in month_map.items():
            inc = data["income"]
            exp = data["expense"]
            sav = inc - exp
            sav_rate = ((sav / inc) * Decimal("100.00")) if inc > 0 else Decimal("0.00")

            trends.append(CashFlowPoint(
                month=m_key,
                income=self._to_float(inc),
                expense=self._to_float(exp),
                savings=self._to_float(sav),
                savings_rate_pct=round(self._to_float(sav_rate), 2)
            ))

        if not trends:
            # Provide current month zero baseline
            cur_key = date.today().strftime("%b %Y")
            trends.append(CashFlowPoint(month=cur_key, income=0.0, expense=0.0, savings=0.0, savings_rate_pct=0.0))

        return trends

    async def get_comprehensive_dashboard(
        self,
        db: AsyncSession,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> ComprehensiveAnalyticsDashboard:
        """
        Assembles all deterministic financial analytics for the dashboard.
        """
        summary = await self.calculate_summary(db, user_id, start_date, end_date)
        mom = await self.calculate_month_over_month(db, user_id, start_date, end_date)
        split = await self.calculate_spending_split(db, user_id, start_date, end_date)
        cat_breakdown = await self.calculate_category_spending(db, user_id, start_date, end_date)
        trends = await self.calculate_trends(db, user_id, start_date, end_date)
        merchants = await self.calculate_top_merchants(db, user_id, start_date, end_date, limit=5)
        budget_util = await self.calculate_budget_utilization(db, user_id, start_date, end_date)

        # Detect recurring subscriptions
        tx_query = select(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.is_subscription == True
        )
        sub_res = await db.execute(tx_query)
        sub_txs = sub_res.scalars().all()
        recurring_items = [
            SubscriptionItem(
                id=st.id,
                service_name=st.merchant_name or st.description,
                amount=float(st.amount),
                billing_cycle="Monthly",
                next_billing_date=st.transaction_date + timedelta(days=30),
                category_name="Subscriptions",
                is_active=True
            )
            for st in sub_txs
        ]

        return ComprehensiveAnalyticsDashboard(
            summary=summary,
            month_over_month=mom,
            spending_split=split,
            category_breakdown=cat_breakdown,
            income_vs_expense_trends=trends,
            largest_merchants=merchants,
            budget_utilization=budget_util,
            recurring_expenses=recurring_items
        )

financial_analytics_engine = FinancialAnalyticsEngine()
