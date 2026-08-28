import pytest
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.ml.forecaster import expense_forecaster

def test_total_monthly_expense_forecasting():
    # Synthetic transactions spanning 30 days
    transactions = [
        {"id": f"t_{i}", "transaction_type": "debit", "category_name": "Food", "amount": 1000.0 + (i * 50), "transaction_date": f"2026-08-{i+1:02d}", "merchant": "Store"}
        for i in range(25)
    ]

    forecast = expense_forecaster.generate_forecast(
        transactions=transactions,
        current_balance=150000.0,
        monthly_income=80000.0,
        currency="INR"
    )

    assert "predicted_monthly_total" in forecast
    assert forecast["predicted_monthly_total"] > 0
    assert "monthly_prediction_interval" in forecast
    interval = forecast["monthly_prediction_interval"]
    assert interval["lower_bound"] <= forecast["predicted_monthly_total"] <= interval["upper_bound"]
    assert 0.0 < forecast["confidence_score"] <= 1.0
    assert len(forecast["major_contributing_factors"]) > 0
    assert len(forecast["human_readable_explanation"]) > 0
    assert len(forecast["forecast_points"]) == 30

def test_category_expense_forecasting():
    transactions = [
        {"id": "c1", "transaction_type": "debit", "category_name": "Food & Dining", "amount": 5000.0, "transaction_date": "2026-08-01"},
        {"id": "c2", "transaction_type": "debit", "category_name": "Food & Dining", "amount": 6000.0, "transaction_date": "2026-08-10"},
        {"id": "c3", "transaction_type": "debit", "category_name": "Housing & Rent", "amount": 20000.0, "transaction_date": "2026-08-05"},
        {"id": "c4", "transaction_type": "debit", "category_name": "Transportation", "amount": 4000.0, "transaction_date": "2026-08-12"}
    ]

    forecast = expense_forecaster.generate_forecast(transactions=transactions, currency="INR")
    cat_forecasts = forecast["category_forecasts"]
    assert len(cat_forecasts) >= 3

    housing = next((c for c in cat_forecasts if c["category_name"] == "Housing & Rent"), None)
    assert housing is not None
    assert housing["predicted_amount"] > 0
    assert housing["percentage_of_total"] > 0
    assert housing["prediction_interval"]["lower_bound"] <= housing["predicted_amount"] <= housing["prediction_interval"]["upper_bound"]

def test_recurring_expense_commitments_projection():
    transactions = [
        {"id": "r1", "transaction_type": "debit", "description": "Netflix Monthly", "amount": 649.0, "transaction_date": "2026-08-01"},
        {"id": "r2", "transaction_type": "debit", "description": "Jio Fiber Broadband", "amount": 999.0, "transaction_date": "2026-08-05"},
        {"id": "r3", "transaction_type": "debit", "description": "Grocery shopping", "amount": 3500.0, "transaction_date": "2026-08-10"}
    ]

    forecast = expense_forecaster.generate_forecast(transactions=transactions, currency="INR")
    rec_forecasts = forecast["recurring_forecasts"]
    assert len(rec_forecasts) >= 2
    assert forecast["total_recurring_projected"] >= 1600.0
    assert forecast["total_variable_projected"] >= 0.0

def test_model_evaluation_holdout_pipeline():
    transactions = [
        {"id": f"t_{i}", "transaction_type": "debit", "amount": float(1000 + (i % 4) * 200), "transaction_date": f"2026-08-{i+1:02d}"}
        for i in range(20)
    ]

    eval_res = expense_forecaster.evaluate_forecast_models(transactions)
    assert "mae" in eval_res
    assert "mape" in eval_res
    assert "rmse" in eval_res
    assert "baseline_mae" in eval_res
    assert "baseline_mape" in eval_res
    assert "baseline_rmse" in eval_res
    assert eval_res["mae"] >= 0.0
    assert eval_res["rmse"] >= 0.0
    assert eval_res["evaluation_holdout_days"] > 0

def test_non_guaranteed_disclaimer_presence():
    forecast = expense_forecaster.generate_forecast([])
    assert "disclaimer" in forecast
    assert "not constitute guaranteed outcomes" in forecast["disclaimer"].lower() or "probabilistic" in forecast["disclaimer"].lower()

@pytest.mark.asyncio
async def test_forecast_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = "forecast_tester@finsight.ai"
        r_reg = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Forecast Tester",
            "preferred_currency": "INR",
            "monthly_income": 95000.0
        })
        assert r_reg.status_code == 200
        token = r_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Add transactions
        for i in range(8):
            await ac.post("/api/v1/transactions/", json={
                "amount": 1500.0 + (i * 100),
                "transaction_type": "debit",
                "transaction_date": f"2026-08-0{i+1}",
                "description": f"Purchase {i}",
                "merchant_name": "Merchant"
            }, headers=headers)

        # 1. GET /api/v1/analytics/forecast
        r_fc = await ac.get("/api/v1/analytics/forecast", headers=headers)
        assert r_fc.status_code == 200
        fc_data = r_fc.json()
        assert "predicted_monthly_total" in fc_data
        assert "monthly_prediction_interval" in fc_data
        assert "confidence_score" in fc_data
        assert "category_forecasts" in fc_data
        assert "disclaimer" in fc_data
        assert "forecast_points" in fc_data

        # 2. GET /api/v1/analytics/forecast/evaluation
        r_eval = await ac.get("/api/v1/analytics/forecast/evaluation", headers=headers)
        assert r_eval.status_code == 200
        eval_data = r_eval.json()
        assert "mae" in eval_data
        assert "mape" in eval_data
        assert "rmse" in eval_data
        assert "baseline_mae" in eval_data
