import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.financial_simulator import financial_simulator

def test_whatif_deterministic_cash_flow_and_annual_savings():
    res = financial_simulator.run_simulation(
        base_income=75000.0,
        base_expenses=35000.0,
        base_balance=150000.0,
        income_change_pct=10.0, # +7,500
        food_spend_reduction=2000.0,
        removed_subscriptions_amount=1500.0,
        extra_goal_contribution=5000.0,
        timeline_months=24
    )

    curr = res["current_scenario"]
    sim = res["simulated_scenario"]

    # Current baseline checks
    assert curr["monthly_income"] == 75000.0
    assert curr["monthly_expenses"] == 35000.0
    assert curr["monthly_net_cash_flow"] == 40000.0
    assert curr["annual_savings"] == 480000.0

    # Simulated scenario checks
    assert sim["monthly_income"] == 82500.0 # 75,000 + 10%
    assert sim["monthly_expenses"] == 31500.0 # 35,000 - 2,000 - 1,500
    assert sim["monthly_net_cash_flow"] == 51000.0 # 82,500 - 31,500
    assert sim["annual_savings"] == 612000.0

    # Deltas
    assert res["net_monthly_delta"] == 11000.0 # +11,000/mo
    assert res["annual_savings_delta"] == 132000.0 # +132,000/yr
    assert res["health_score_delta"] >= 0

def test_whatif_goal_acceleration_impact():
    active_goals = [
        {
            "title": "MacBook Pro M-Series",
            "target_amount": 80000.0,
            "current_amount": 23000.0,
            "monthly_saving": 14250.0 # remaining: 57,000 / 14,250 = 4 months
        }
    ]

    res = financial_simulator.run_simulation(
        base_income=75000.0,
        base_expenses=35000.0,
        income_change_pct=10.0,
        food_spend_reduction=2000.0,
        extra_goal_contribution=5000.0,
        active_goals=active_goals
    )

    goal_impact = res["goal_impacts"][0]
    assert goal_impact["goal_title"] == "MacBook Pro M-Series"
    assert goal_impact["baseline_months_to_complete"] == 4
    assert goal_impact["simulated_months_to_complete"] < 4
    assert goal_impact["months_saved"] >= 1
    assert "2026" in goal_impact["accelerated_completion_date"] or "2027" in goal_impact["accelerated_completion_date"]

def test_whatif_ai_explanation_contains_exact_numbers():
    res = financial_simulator.run_simulation(
        base_income=75000.0,
        base_expenses=35000.0,
        food_spend_reduction=2000.0,
        currency="INR"
    )

    exp = res["ai_explanation"]
    assert "2,000.00" in exp
    assert "24,000.00" in exp

@pytest.mark.asyncio
async def test_simulation_api_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = "sim_user@finsight.ai"
        r_reg = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Sim User",
            "preferred_currency": "INR",
            "monthly_income": 75000.0
        })
        assert r_reg.status_code == 200
        token = r_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Call simulation endpoint
        r_sim = await ac.post("/api/v1/analytics/simulation", json={
            "income_change_pct": 10.0,
            "food_spend_reduction": 2000.0,
            "removed_subscriptions_amount": 1500.0,
            "extra_goal_contribution": 5000.0,
            "timeline_months": 24
        }, headers=headers)

        assert r_sim.status_code == 200
        data = r_sim.json()
        assert "current_scenario" in data
        assert "simulated_scenario" in data
        assert data["net_monthly_delta"] == 11000.0
        assert data["annual_savings_delta"] == 132000.0
        assert "guru_critique" in data
        assert len(data["simulated_timeline"]) == 24
