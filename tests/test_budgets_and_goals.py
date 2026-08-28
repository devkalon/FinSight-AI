import pytest
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_budget_creation_and_threshold_warnings():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = "budget_user@finsight.ai"
        r_reg = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Budget User",
            "preferred_currency": "INR",
            "monthly_income": 80000.0
        })
        assert r_reg.status_code == 200
        token = r_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Fetch categories
        r_cats = await ac.get("/api/v1/transactions/categories", headers=headers)
        assert r_cats.status_code == 200
        categories = r_cats.json()
        assert len(categories) > 0
        cat_id = categories[0]["id"]

        # 2. Create budget with 80% alert threshold
        r_b_create = await ac.post("/api/v1/budgets/", json={
            "category_id": cat_id,
            "monthly_limit": 10000.0,
            "alert_threshold_percentage": 80
        }, headers=headers)
        assert r_b_create.status_code == 200
        b_data = r_b_create.json()
        assert b_data["monthly_limit"] == 10000.0
        budget_id = b_data["id"]

        # 3. Add transactions totaling ₹8,500 (85% utilization - should trigger warning)
        await ac.post("/api/v1/transactions/", json={
            "amount": 8500.0,
            "transaction_type": "debit",
            "transaction_date": date.today().isoformat(),
            "description": "Category spend",
            "category_id": cat_id
        }, headers=headers)

        # 4. List budgets and verify warning status
        r_b_list = await ac.get("/api/v1/budgets/", headers=headers)
        assert r_b_list.status_code == 200
        budgets = r_b_list.json()
        matched = next((b for b in budgets if b["id"] == budget_id), None)
        assert matched is not None
        assert matched["spent_amount"] == 8500.0
        assert matched["spent_percentage"] == 85.0
        assert matched["warning_status"] == "warning"
        assert matched["warning_message"] is not None
        assert "Threshold Warning" in matched["warning_message"]

        # 5. Add additional transaction to exceed budget (₹12,000 total - critical overbudget)
        await ac.post("/api/v1/transactions/", json={
            "amount": 3500.0,
            "transaction_type": "debit",
            "transaction_date": date.today().isoformat(),
            "description": "Exceeding budget spend",
            "category_id": cat_id
        }, headers=headers)

        r_b_list2 = await ac.get("/api/v1/budgets/", headers=headers)
        matched2 = next((b for b in r_b_list2.json() if b["id"] == budget_id), None)
        assert matched2["spent_amount"] == 12000.0
        assert matched2["is_over_budget"] is True
        assert matched2["warning_status"] == "critical_overbudget"

        # 6. Historical Performance & Warnings Endpoints
        r_perf = await ac.get("/api/v1/budgets/historical-performance", headers=headers)
        assert r_perf.status_code == 200
        assert r_perf.json()["active_warnings_count"] >= 1

        r_warns = await ac.get("/api/v1/budgets/warnings", headers=headers)
        assert r_warns.status_code == 200
        assert len(r_warns.json()) >= 1

@pytest.mark.asyncio
async def test_goal_deterministic_calculations_and_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = "goal_user@finsight.ai"
        r_reg = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Goal User",
            "preferred_currency": "INR",
            "monthly_income": 90000.0
        })
        assert r_reg.status_code == 200
        token = r_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Target: ₹80,000, Current: ₹23,000, Target Date: ~4 months ahead
        today = date.today()
        # Set target date exactly 4 months ahead
        month = (today.month + 4) % 12 or 12
        year = today.year + ((today.month + 4 - 1) // 12)
        target_date = date(year, month, 28)

        # 1. Create Laptop Purchase Goal
        r_g_create = await ac.post("/api/v1/goals/", json={
            "title": "MacBook Pro M-Series",
            "category": "Laptop Purchase",
            "target_amount": 80000.0,
            "current_amount": 23000.0,
            "target_date": target_date.isoformat(),
            "expected_return_rate": 12.0
        }, headers=headers)
        assert r_g_create.status_code == 200
        goal = r_g_create.json()
        goal_id = goal["id"]
        assert goal["target_amount"] == 80000.0
        assert goal["current_amount"] == 23000.0
        assert goal["remaining_amount"] == 57000.0
        assert goal["months_remaining"] == 4
        assert goal["required_monthly_saving"] == 14250.0 # 57,000 / 4
        assert 28.7 <= goal["progress_percentage"] <= 28.8
        assert goal["projected_completion_date"] is not None
        assert goal["ai_recommendation"] is not None

        # 2. Test Goal Categories: Emergency Fund, Travel, Education
        categories = ["Emergency Fund", "Travel", "Education"]
        for cat in categories:
            r_cat_g = await ac.post("/api/v1/goals/", json={
                "title": f"Test {cat} Goal",
                "category": cat,
                "target_amount": 100000.0,
                "current_amount": 10000.0,
                "target_date": date(year + 1, month, 1).isoformat()
            }, headers=headers)
            assert r_cat_g.status_code == 200
            assert r_cat_g.json()["category"] == cat

        # 3. Contribute to Goal
        r_contrib = await ac.post(f"/api/v1/goals/{goal_id}/contribute", json={
            "amount": 57000.0
        }, headers=headers)
        assert r_contrib.status_code == 200
        updated_goal = r_contrib.json()
        assert updated_goal["current_amount"] == 80000.0
        assert updated_goal["progress_percentage"] == 100.0
        assert updated_goal["status"] == "achieved"

        # 4. Delete Goal
        r_del = await ac.delete(f"/api/v1/goals/{goal_id}", headers=headers)
        assert r_del.status_code == 200
