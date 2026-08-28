import pytest
import uuid
from decimal import Decimal
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import User, Profile
from backend.app.models.category import Category
from backend.app.models.transaction import Transaction
from backend.app.models.budget import Budget
from backend.app.services.financial_analytics import financial_analytics_engine

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

async def create_deterministic_analytics_user(db):
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"analytics_{uuid.uuid4().hex[:8]}@finsight.ai",
        hashed_password="hashed_pw_test",
        is_active=True
    )
    db.add(user)

    profile = Profile(
        id=str(uuid.uuid4()),
        user_id=user_id,
        full_name="Analytics Tester",
        preferred_currency="INR",
        monthly_income=75000.0
    )
    db.add(profile)

    # Categories
    cat_rent = Category(id=str(uuid.uuid4()), name="Rent", group_type="Need", color="#EF4444")
    cat_food = Category(id=str(uuid.uuid4()), name="Food", group_type="Need", color="#10B981")
    cat_bills = Category(id=str(uuid.uuid4()), name="Bills", group_type="Need", color="#F59E0B")
    cat_shop = Category(id=str(uuid.uuid4()), name="Shopping", group_type="Want", color="#8B5CF6")
    cat_inv = Category(id=str(uuid.uuid4()), name="Investment", group_type="Investment", color="#059669")
    db.add_all([cat_rent, cat_food, cat_bills, cat_shop, cat_inv])

    today = date.today()
    # Income Transactions
    t1 = Transaction(
        id=str(uuid.uuid4()), user_id=user_id, amount=50000.0, transaction_type="credit",
        transaction_date=today - timedelta(days=5), description="Tech Corp Monthly Salary",
        source="manual", confidence_score=1.0, is_deleted=False
    )
    t2 = Transaction(
        id=str(uuid.uuid4()), user_id=user_id, amount=25000.0, transaction_type="credit",
        transaction_date=today - timedelta(days=2), description="Consulting Milestone Credit",
        source="manual", confidence_score=1.0, is_deleted=False
    )

    # Expense Transactions (Total = 30,000)
    # Rent = 15,000 (Essential)
    t3 = Transaction(
        id=str(uuid.uuid4()), user_id=user_id, category_id=cat_rent.id, amount=15000.0,
        transaction_type="debit", transaction_date=today - timedelta(days=10),
        description="Apartment Rent Transfer", merchant_name="Landlord Realty",
        source="manual", confidence_score=1.0, is_deleted=False
    )
    # Food/Groceries = 5,000 (Essential)
    t4 = Transaction(
        id=str(uuid.uuid4()), user_id=user_id, category_id=cat_food.id, amount=5000.0,
        transaction_type="debit", transaction_date=today - timedelta(days=4),
        description="BigBasket Weekly Groceries", merchant_name="BigBasket",
        source="manual", confidence_score=1.0, is_deleted=False
    )
    # Bills = 4,000 (Essential)
    t5 = Transaction(
        id=str(uuid.uuid4()), user_id=user_id, category_id=cat_bills.id, amount=4000.0,
        transaction_type="debit", transaction_date=today - timedelta(days=3),
        description="Bescom Power Bill", merchant_name="Bescom",
        source="manual", confidence_score=1.0, is_deleted=False
    )
    # Shopping = 6,000 (Discretionary)
    t6 = Transaction(
        id=str(uuid.uuid4()), user_id=user_id, category_id=cat_shop.id, amount=6000.0,
        transaction_type="debit", transaction_date=today - timedelta(days=1),
        description="Amazon Retail Order", merchant_name="Amazon India",
        source="manual", confidence_score=1.0, is_deleted=False
    )

    # Budget
    b1 = Budget(
        id=str(uuid.uuid4()), user_id=user_id, category_id=cat_rent.id,
        monthly_limit=20000.0, is_active=True
    )
    b2 = Budget(
        id=str(uuid.uuid4()), user_id=user_id, category_id=cat_shop.id,
        monthly_limit=5000.0, is_active=True
    )

    db.add_all([t1, t2, t3, t4, t5, t6, b1, b2])
    await db.commit()
    return user_id

@pytest.mark.asyncio
async def test_deterministic_summary_and_savings_rate():
    await init_db()
    async with AsyncSessionLocal() as db:
        user_id = await create_deterministic_analytics_user(db)
        
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

        summary = await financial_analytics_engine.calculate_summary(db, user_id, start_date, end_date)

        # Expected:
        # Income = 50,000 + 25,000 = 75,000.0
        # Expense = 15,000 + 5,000 + 4,000 + 6,000 = 30,000.0
        # Savings = 75,000 - 30,000 = 45,000.0
        # Savings Rate = (45,000 / 75,000) * 100 = 60.0%
        assert summary.total_income == 75000.0
        assert summary.total_expenses == 30000.0
        assert summary.net_savings == 45000.0
        assert summary.savings_rate_pct == 60.0
        assert summary.transaction_count == 6
        assert summary.days_in_period == 31
        assert summary.average_daily_spending == round(30000.0 / 31, 2)

@pytest.mark.asyncio
async def test_deterministic_spending_split():
    async with AsyncSessionLocal() as db:
        user_id = await create_deterministic_analytics_user(db)
        
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

        split = await financial_analytics_engine.calculate_spending_split(db, user_id, start_date, end_date)

        # Essential = Rent (15,000) + Food (5,000) + Bills (4,000) = 24,000.0 (80.0%)
        # Discretionary = Shopping (6,000) = 6,000.0 (20.0%)
        assert split.essential_amount == 24000.0
        assert split.essential_pct == 80.0
        assert split.discretionary_amount == 6000.0
        assert split.discretionary_pct == 20.0

@pytest.mark.asyncio
async def test_deterministic_top_merchants_and_budget_utilization():
    async with AsyncSessionLocal() as db:
        user_id = await create_deterministic_analytics_user(db)
        
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

        # Top merchants
        merchants = await financial_analytics_engine.calculate_top_merchants(db, user_id, start_date, end_date, limit=3)
        assert len(merchants) == 3
        assert merchants[0].merchant_name == "Landlord Realty"
        assert merchants[0].total_amount == 15000.0
        assert merchants[1].merchant_name == "Amazon India"
        assert merchants[1].total_amount == 6000.0

        # Budget Utilization
        budgets = await financial_analytics_engine.calculate_budget_utilization(db, user_id, start_date, end_date)
        assert len(budgets) == 2

        # Rent budget: Limit 20,000, Spent 15,000 (75.0%)
        rent_b = next(b for b in budgets if b.category_name == "Rent")
        assert rent_b.budgeted_amount == 20000.0
        assert rent_b.spent_amount == 15000.0
        assert rent_b.utilization_pct == 75.0
        assert rent_b.remaining_amount == 5000.0
        assert rent_b.is_over_budget is False

        # Shopping budget: Limit 5,000, Spent 6,000 (120.0%) -> Over Budget
        shop_b = next(b for b in budgets if b.category_name == "Shopping")
        assert shop_b.budgeted_amount == 5000.0
        assert shop_b.spent_amount == 6000.0
        assert shop_b.utilization_pct == 120.0
        assert shop_b.is_over_budget is True

@pytest.mark.asyncio
async def test_comprehensive_analytics_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"api_analytics_{uuid.uuid4().hex[:8]}@finsight.ai"
        res_reg = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": "SecurePassword123!",
            "full_name": "API Analytics Tester",
            "preferred_currency": "INR",
            "monthly_income": 85000.0
        })
        assert res_reg.status_code == 200
        token = res_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Summary API
        res_summary = await ac.get("/api/v1/analytics/summary", headers=headers)
        assert res_summary.status_code == 200
        data_summary = res_summary.json()
        assert "total_income" in data_summary
        assert "total_expenses" in data_summary
        assert "savings_rate_pct" in data_summary

        # 2. Dashboard API
        res_dash = await ac.get("/api/v1/analytics/dashboard", headers=headers)
        assert res_dash.status_code == 200
        data_dash = res_dash.json()
        assert "summary" in data_dash
        assert "month_over_month" in data_dash
        assert "spending_split" in data_dash
        assert "category_breakdown" in data_dash
        assert "income_vs_expense_trends" in data_dash
        assert "largest_merchants" in data_dash
        assert "budget_utilization" in data_dash
