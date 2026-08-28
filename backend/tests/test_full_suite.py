import pytest
import asyncio
from datetime import date
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import init_db
from backend.app.core.pii_scrubber import pii_scrubber
from backend.app.services.ai.tools import financial_tools
from backend.app.services.ml.categorizer import expense_categorizer
from backend.app.services.ml.anomaly_detector import anomaly_detector
from backend.app.services.ml.forecaster import expense_forecaster
from backend.app.services.financial_health import financial_health_engine
from backend.app.services.ai.gurus import guru_engine
from backend.app.services.ai.agent import financial_advisor_agent

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

@pytest.mark.asyncio
async def test_database_initialization():
    await init_db()

@pytest.mark.asyncio
async def test_pii_scrubber():
    text = "Payment received from user@example.com with PAN ABCDE1234F and Card 4111-2222-3333-4444. Phone: 9876543210"
    scrubbed, stats = pii_scrubber.scrub_text(text)
    assert "[REDACTED_EMAIL]" in scrubbed
    assert "[REDACTED_PAN]" in scrubbed
    assert "[REDACTED_CARD]" in scrubbed
    assert "user@example.com" not in scrubbed

@pytest.mark.asyncio
async def test_financial_tools():
    # SIP Test
    sip = financial_tools.calculate_sip(monthly_investment=10000, annual_rate_pct=12.0, years=10)
    assert sip["total_invested"] == 1200000.0
    assert sip["total_maturity_value"] > 2200000.0

    # EMI Test
    emi = financial_tools.calculate_emi(principal=1000000, annual_interest_rate=9.0, tenure_years=5)
    assert emi["monthly_emi"] > 20000.0

    # Emergency fund
    ef = financial_tools.calculate_emergency_fund_target(monthly_expenses=40000, target_months=6)
    assert ef["ideal_emergency_fund"] == 240000.0

@pytest.mark.asyncio
async def test_ml_categorizer():
    cat1 = expense_categorizer.categorize("Swiggy Biryani Delivery")
    assert cat1 in ["Food", "Food & Dining"]

    cat2 = expense_categorizer.categorize("Uber Premier Trip Fare")
    assert cat2 in ["Transport", "Transportation"]

    cat3 = expense_categorizer.categorize("Monthly Netflix Subscription")
    assert cat3 in ["Subscriptions", "Entertainment"]

@pytest.mark.asyncio
async def test_financial_health_engine():
    health = financial_health_engine.calculate_health_score(
        monthly_income=100000.0,
        monthly_expenses=35000.0,
        total_savings=300000.0,
        budget_limit=50000.0
    )
    assert health["score"] >= 80
    assert health["rating"] in ["Good", "Excellent"]
    assert len(health["insights"]) > 0

@pytest.mark.asyncio
async def test_multi_guru_engine():
    comparison = guru_engine.get_guru_comparison("Should I buy a luxury sports car on EMI?")
    assert "buffett" in comparison["opinions"]
    assert "kiyosaki" in comparison["opinions"]
    assert "sethi" in comparison["opinions"]
    assert "indian_expert" in comparison["opinions"]

@pytest.mark.asyncio
async def test_ai_agent_tool_execution():
    res = await financial_advisor_agent.process_query(
        user_query="If I invest 15000 per month in SIP for 15 years, what will be my return?",
        persona="buffett"
    )
    assert "tool_calls" in res
    assert len(res["tool_calls"]) > 0
    assert "SIP" in res["response"]

@pytest.mark.asyncio
async def test_auth_and_transactions_e2e():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Health check
        res = await ac.get("/health")
        assert res.status_code == 200

        import uuid
        unique_email = f"testfin_{uuid.uuid4().hex[:8]}@finsight.ai"

        # Register user
        reg_payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Test Fintech User",
            "preferred_currency": "INR",
            "monthly_income": 95000.0
        }
        r_reg = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert r_reg.status_code == 200
        token = r_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Fetch Categories
        r_cats = await ac.get("/api/v1/transactions/categories", headers=headers)
        assert r_cats.status_code == 200
        cats = r_cats.json()
        assert len(cats) >= 5

        # Create Transaction
        tx_payload = {
            "amount": 1450.0,
            "transaction_type": "debit",
            "transaction_date": date.today().isoformat(),
            "description": "Starbucks Coffee & Snacks",
            "payment_method": "UPI"
        }
        r_tx = await ac.post("/api/v1/transactions/", json=tx_payload, headers=headers)
        assert r_tx.status_code == 200
        tx_data = r_tx.json()
        assert tx_data["amount"] == 1450.0

        # Create Budget
        cat_id = cats[0]["id"]
        budget_payload = {
            "category_id": cat_id,
            "monthly_limit": 10000.0,
            "alert_threshold_percentage": 80
        }
        r_b = await ac.post("/api/v1/budgets/", json=budget_payload, headers=headers)
        assert r_b.status_code == 200

        # Create Goal
        goal_payload = {
            "title": "Emergency Fund Corpus",
            "target_amount": 300000.0,
            "current_amount": 50000.0,
            "target_date": "2027-12-31",
            "expected_return_rate": 12.0
        }
        r_g = await ac.post("/api/v1/goals/", json=goal_payload, headers=headers)
        assert r_g.status_code == 200

        # Chat with Advisor
        chat_payload = {
            "message": "How should I structure my monthly budget?",
            "persona": "sethi"
        }
        r_chat = await ac.post("/api/v1/advisor/chat", json=chat_payload, headers=headers)
        assert r_chat.status_code == 200
        assert "content" in r_chat.json()
