import pytest
from datetime import date
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.monthly_report_engine import monthly_report_engine

def test_monthly_report_deterministic_11_sections_metrics():
    transactions = [
        {"description": "Tech Consulting Income", "amount": 75000.0, "transaction_type": "credit", "transaction_date": "2026-08-01", "category_name": "Income"},
        {"description": "Apartment Rent", "amount": 18000.0, "transaction_type": "debit", "transaction_date": "2026-08-02", "category_name": "Rent"},
        {"description": "Swiggy Food Delivery", "amount": 4200.0, "transaction_type": "debit", "transaction_date": "2026-08-05", "category_name": "Food & Dining"},
        {"description": "Jio Fiber Broadband", "amount": 825.0, "transaction_type": "debit", "transaction_date": "2026-08-10", "category_name": "Bills"},
        {"description": "Amazon Shopping", "amount": 3500.0, "transaction_type": "debit", "transaction_date": "2026-08-15", "category_name": "Shopping"}
    ]
    budgets = [
        {"category_name": "Food & Dining", "monthly_limit": 8000.0, "spent_amount": 4200.0, "is_over_budget": False},
        {"category_name": "Shopping", "monthly_limit": 5000.0, "spent_amount": 3500.0, "is_over_budget": False}
    ]
    goals = [
        {"title": "Emergency Fund", "target_amount": 100000.0, "current_amount": 60000.0, "progress_percentage": 60.0, "required_monthly_saving": 10000.0, "projected_completion_date": "December 2026"}
    ]
    anomalies = [
        {"title": "Dining Surge", "severity": "medium", "explanation": "Weekend restaurant cluster."}
    ]
    subscriptions = [
        {"service_name": "Netflix", "amount": 649.0, "billing_cycle": "monthly", "annualized_cost": 7788.0}
    ]

    report = monthly_report_engine.generate_report(
        month_str="2026-08",
        user_name="Kalon Test",
        transactions=transactions,
        budgets=budgets,
        goals=goals,
        anomalies=anomalies,
        subscriptions=subscriptions,
        user_income=75000.0,
        currency="INR"
    )

    m = report.metrics
    n = report.narrative

    # 1. Exact numbers verification
    assert m.total_income == 75000.0
    assert m.total_expenses == 18000.0 + 4200.0 + 825.0 + 3500.0 # 26,525.0
    assert m.net_savings == 75000.0 - 26525.0 # 48,475.0
    assert m.savings_rate_pct == round((48475.0 / 75000.0) * 100.0, 1) # 64.6%
    assert len(m.spending_by_category) >= 4
    assert m.active_goals_count == 1
    assert m.recurring_annual_total == 7788.0

    # 2. All 11 narrative sections check
    assert n.executive_summary is not None
    assert n.income_narrative is not None
    assert n.spending_narrative is not None
    assert n.savings_narrative is not None
    assert n.budget_narrative is not None
    assert n.goal_narrative is not None
    assert n.anomalies_narrative is not None
    assert n.recurring_narrative is not None
    assert n.forecast_narrative is not None
    assert len(n.key_observations) >= 3
    assert len(n.recommended_actions) >= 3

    # 3. Exact narrative grounding (numbers match exact calculations)
    assert "75,000.00" in n.executive_summary
    assert "26,525.00" in n.executive_summary
    assert "48,475.00" in n.executive_summary

def test_monthly_report_pdf_generation():
    transactions = [
        {"description": "Salary", "amount": 75000.0, "transaction_type": "credit", "transaction_date": "2026-08-01", "category_name": "Income"},
        {"description": "Rent", "amount": 18000.0, "transaction_type": "debit", "transaction_date": "2026-08-02", "category_name": "Rent"}
    ]
    report = monthly_report_engine.generate_report(
        month_str="2026-08",
        user_name="Kalon Test",
        transactions=transactions,
        budgets=[],
        goals=[],
        anomalies=[],
        subscriptions=[],
        user_income=75000.0,
        currency="INR"
    )

    pdf_bytes = monthly_report_engine.generate_pdf(report)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")

@pytest.mark.asyncio
async def test_monthly_report_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = "report_user@finsight.ai"
        r_reg = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Report User",
            "preferred_currency": "INR",
            "monthly_income": 75000.0
        })
        assert r_reg.status_code == 200
        token = r_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Fetch JSON Monthly Report
        r_rep = await ac.get("/api/v1/reports/monthly?month=2026-08", headers=headers)
        assert r_rep.status_code == 200
        data = r_rep.json()
        assert "metrics" in data
        assert "narrative" in data
        assert data["metrics"]["month"] == "2026-08"
        assert len(data["narrative"]["key_observations"]) >= 3
        assert len(data["narrative"]["recommended_actions"]) >= 3

        # 2. Download Monthly Report PDF
        r_pdf = await ac.get("/api/v1/reports/monthly/pdf?month=2026-08", headers=headers)
        assert r_pdf.status_code == 200
        assert r_pdf.headers["content-type"] == "application/pdf"
        assert len(r_pdf.content) > 500
        assert r_pdf.content.startswith(b"%PDF")
