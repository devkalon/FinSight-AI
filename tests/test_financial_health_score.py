import pytest
import uuid
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import User, Profile
from backend.app.models.category import Category
from backend.app.models.transaction import Transaction
from backend.app.models.budget import Budget
from backend.app.models.goal import FinancialGoal
from backend.app.services.financial_health import financial_health_engine

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

async def create_health_test_user(db, income=80000.0):
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"health_{uuid.uuid4().hex[:8]}@finsight.ai",
        hashed_password="pw_test",
        is_active=True
    )
    db.add(user)

    profile = Profile(
        id=str(uuid.uuid4()),
        user_id=user_id,
        full_name="Health Test User",
        preferred_currency="INR",
        monthly_income=income
    )
    db.add(profile)
    await db.commit()
    return user_id

@pytest.mark.asyncio
async def test_deterministic_health_score_components():
    await init_db()
    async with AsyncSessionLocal() as db:
        user_id = await create_health_test_user(db, income=100000.0)

        # Add categories
        cat_emi = Category(id=str(uuid.uuid4()), name="EMI", group_type="Need", color="#EF4444")
        cat_food = Category(id=str(uuid.uuid4()), name="Food", group_type="Need", color="#10B981")
        cat_sub = Category(id=str(uuid.uuid4()), name="Subscriptions", group_type="Want", color="#8B5CF6")
        db.add_all([cat_emi, cat_food, cat_sub])

        today = date.today()
        # Add income: 100,000
        t_inc = Transaction(
            id=str(uuid.uuid4()), user_id=user_id, amount=100000.0, transaction_type="credit",
            transaction_date=today - timedelta(days=2), description="Salary Credit", is_deleted=False
        )
        # Add expenses: Total 35,000 (Savings = 65,000 -> 65% savings rate)
        # EMI = 10,000 (10% DTI)
        t_emi = Transaction(
            id=str(uuid.uuid4()), user_id=user_id, category_id=cat_emi.id, amount=10000.0,
            transaction_type="debit", transaction_date=today - timedelta(days=5),
            description="Car Loan Monthly EMI", is_deleted=False
        )
        # Food = 20,000
        t_food = Transaction(
            id=str(uuid.uuid4()), user_id=user_id, category_id=cat_food.id, amount=20000.0,
            transaction_type="debit", transaction_date=today - timedelta(days=10),
            description="Supermarket Groceries", is_deleted=False
        )
        # Subscriptions = 5,000 (5% Recurring)
        t_sub = Transaction(
            id=str(uuid.uuid4()), user_id=user_id, category_id=cat_sub.id, amount=5000.0,
            transaction_type="debit", transaction_date=today - timedelta(days=12),
            description="Software Subscriptions", is_subscription=True, is_deleted=False
        )
        # Budget: 40,000 Limit (Spent 35,000 -> 87.5% utilized)
        b = Budget(id=str(uuid.uuid4()), user_id=user_id, monthly_limit=40000.0, is_active=True)

        # Goal: Emergency Fund
        g = FinancialGoal(
            id=str(uuid.uuid4()), user_id=user_id, title="Emergency Fund",
            target_amount=200000.0, current_amount=120000.0, target_date=today + timedelta(days=180),
            status="in_progress"
        )

        db.add_all([t_inc, t_emi, t_food, t_sub, b, g])
        await db.commit()

        # Compute Score
        res = await financial_health_engine.compute_health_score(db, user_id, persist=True)

        assert 0 <= res.score <= 100
        assert res.rating in ["Excellent", "Good"]
        assert len(res.components) == 7
        assert "savings_rate" in res.components
        assert "budget_adherence" in res.components
        assert "debt_burden" in res.components
        assert "emergency_fund" in res.components
        assert "spending_consistency" in res.components
        assert "recurring_burden" in res.components
        assert "goal_progress" in res.components

        # Savings rate is 65% >= 35% -> score = 100
        assert res.components["savings_rate"].score == 100
        # Debt burden is 10% DTI <= 15% -> score >= 90
        assert res.components["debt_burden"].score >= 90
        # Positive factors present
        assert len(res.positive_factors) > 0

@pytest.mark.asyncio
async def test_edge_case_high_debt_and_overspending():
    async with AsyncSessionLocal() as db:
        user_id = await create_health_test_user(db, income=50000.0)
        today = date.today()

        # Overspending: Income 50,000, Expenses 60,000 (Negative savings)
        # High Debt: 30,000 EMI (60% DTI)
        t_inc = Transaction(
            id=str(uuid.uuid4()), user_id=user_id, amount=50000.0, transaction_type="credit",
            transaction_date=today - timedelta(days=1), description="Salary", is_deleted=False
        )
        t_debt = Transaction(
            id=str(uuid.uuid4()), user_id=user_id, amount=30000.0, transaction_type="debit",
            transaction_date=today - timedelta(days=5), description="Personal Loan EMI", is_deleted=False
        )
        t_exp = Transaction(
            id=str(uuid.uuid4()), user_id=user_id, amount=30000.0, transaction_type="debit",
            transaction_date=today - timedelta(days=10), description="Discretionary Spend", is_deleted=False
        )
        db.add_all([t_inc, t_debt, t_exp])
        await db.commit()

        res = await financial_health_engine.compute_health_score(db, user_id, persist=False)
        assert res.components["savings_rate"].score == 10 # Overspending penalty
        assert res.components["debt_burden"].score <= 40 # Severe DTI penalty
        assert len(res.negative_factors) > 0
        assert len(res.recommendations) > 0

@pytest.mark.asyncio
async def test_health_score_history_and_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"health_api_{uuid.uuid4().hex[:8]}@finsight.ai"
        reg = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "API Health Tester",
            "preferred_currency": "INR",
            "monthly_income": 90000.0
        })
        assert reg.status_code == 200
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Fetch Health Score
        res_score = await ac.get("/api/v1/analytics/health-score", headers=headers)
        assert res_score.status_code == 200
        data_score = res_score.json()
        assert "score" in data_score
        assert "components" in data_score
        assert "positive_factors" in data_score
        assert "recommendations" in data_score
        assert "delta_explanation" in data_score

        # 2. Fetch Health Score History
        res_hist = await ac.get("/api/v1/analytics/health-score/history", headers=headers)
        assert res_hist.status_code == 200
        data_hist = res_hist.json()
        assert "history" in data_hist
        assert len(data_hist["history"]) >= 1
        assert data_hist["history"][0]["score"] == data_score["score"]
