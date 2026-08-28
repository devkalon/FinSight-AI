import pytest
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.ml.subscription_tracker import subscription_tracker

def test_detect_monthly_and_annual_subscriptions():
    today = date.today()
    txs = [
        {"description": "Netflix.com Monthly Sub", "amount": 649.0, "transaction_date": (today - timedelta(days=20)).isoformat(), "transaction_type": "debit"},
        {"description": "Spotify India Premium", "amount": 179.0, "transaction_date": (today - timedelta(days=10)).isoformat(), "transaction_type": "debit"},
        {"description": "Amazon Prime Annual Membership", "amount": 1499.0, "transaction_date": (today - timedelta(days=100)).isoformat(), "transaction_type": "debit"},
        {"description": "Jio Fiber Broadband 100M", "amount": 825.0, "transaction_date": (today - timedelta(days=15)).isoformat(), "transaction_type": "debit"},
        {"description": "Cult.fit Elite Monthly", "amount": 1750.0, "transaction_date": (today - timedelta(days=5)).isoformat(), "transaction_type": "debit"}
    ]

    detected = subscription_tracker.detect_subscriptions(txs)
    names = [d["service_name"] for d in detected]
    
    assert "Netflix Premium" in names
    assert "Spotify Family" in names
    assert "Amazon Prime Annual" in names
    assert "Jio Fiber Broadband" in names
    assert "Cult.fit Elite Membership" in names

    # Check annualized cost calculations
    netflix = next(d for d in detected if d["service_name"] == "Netflix Premium")
    assert netflix["recurring_type"] == "monthly_subscription"
    assert netflix["annualized_cost"] == 649.0 * 12

    prime = next(d for d in detected if d["service_name"] == "Amazon Prime Annual")
    assert prime["recurring_type"] == "annual_subscription"
    assert prime["annualized_cost"] == 1499.0

def test_anti_false_positive_guardrail_rejects_random_purchases():
    today = date.today()
    # Random purchases with erratic amounts and random dates (Swiggy, Groceries, Fuel)
    random_txs = [
        {"description": "Swiggy Order #123", "amount": 420.0, "transaction_date": (today - timedelta(days=2)).isoformat(), "transaction_type": "debit"},
        {"description": "Swiggy Order #456", "amount": 890.0, "transaction_date": (today - timedelta(days=5)).isoformat(), "transaction_type": "debit"},
        {"description": "Swiggy Order #789", "amount": 230.0, "transaction_date": (today - timedelta(days=11)).isoformat(), "transaction_type": "debit"},
        {"description": "Blinkit Quick Groceries", "amount": 650.0, "transaction_date": (today - timedelta(days=3)).isoformat(), "transaction_type": "debit"},
        {"description": "Blinkit Quick Groceries", "amount": 1240.0, "transaction_date": (today - timedelta(days=8)).isoformat(), "transaction_type": "debit"},
        {"description": "Shell Petrol Station Fuel", "amount": 1500.0, "transaction_date": (today - timedelta(days=7)).isoformat(), "transaction_type": "debit"},
        {"description": "Shell Petrol Station Fuel", "amount": 2200.0, "transaction_date": (today - timedelta(days=19)).isoformat(), "transaction_type": "debit"}
    ]

    detected = subscription_tracker.detect_subscriptions(random_txs)
    service_names = [d["service_name"].lower() for d in detected]
    
    # Assert Swiggy, Blinkit, and Shell are NOT classified as subscriptions
    assert not any("swiggy" in name for name in service_names)
    assert not any("blinkit" in name for name in service_names)
    assert not any("shell" in name for name in service_names)

def test_heuristic_uncatalogued_recurring_detection():
    today = date.today()
    # Custom monthly service with consistent amount and exact 30-day cadence
    custom_txs = [
        {"description": "Private Cloud VPS Hosting", "amount": 1200.0, "transaction_date": (today - timedelta(days=60)).isoformat(), "transaction_type": "debit"},
        {"description": "Private Cloud VPS Hosting", "amount": 1200.0, "transaction_date": (today - timedelta(days=30)).isoformat(), "transaction_type": "debit"},
        {"description": "Private Cloud VPS Hosting", "amount": 1200.0, "transaction_date": today.isoformat(), "transaction_type": "debit"}
    ]

    detected = subscription_tracker.detect_subscriptions(custom_txs)
    matched = next((d for d in detected if "Private Cloud" in d["service_name"]), None)
    assert matched is not None
    assert matched["amount"] == 1200.0
    assert matched["billing_cycle"] == "monthly"
    assert matched["annualized_cost"] == 14400.0
    assert matched["status"] == "detected"

@pytest.mark.asyncio
async def test_subscriptions_api_endpoints_and_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = "sub_user@finsight.ai"
        r_reg = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Sub User",
            "preferred_currency": "INR"
        })
        assert r_reg.status_code == 200
        token = r_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Fetch dashboard
        r_dash = await ac.get("/api/v1/subscriptions/", headers=headers)
        assert r_dash.status_code == 200
        data = r_dash.json()
        assert "total_monthly_recurring" in data
        assert "total_annual_recurring" in data
        assert data["total_monthly_recurring"] > 0
        assert len(data["subscriptions"]) > 0
        
        sub_id = data["subscriptions"][0]["id"]

        # 2. Confirm subscription
        r_conf = await ac.post(f"/api/v1/subscriptions/{sub_id}/confirm", headers=headers)
        assert r_conf.status_code == 200
        assert r_conf.json()["status"] == "confirmed"

        # 3. Edit subscription
        r_edit = await ac.put(f"/api/v1/subscriptions/{sub_id}", json={
            "amount": 799.0,
            "service_name": "Netflix 4K Ultra"
        }, headers=headers)
        assert r_edit.status_code == 200
        assert r_edit.json()["amount"] == 799.0
        assert r_edit.json()["service_name"] == "Netflix 4K Ultra"

        # 4. Dismiss subscription
        r_dism = await ac.post(f"/api/v1/subscriptions/{sub_id}/dismiss", headers=headers)
        assert r_dism.status_code == 200
        assert r_dism.json()["status"] == "dismissed"
        assert r_dism.json()["is_active"] is False

        # 5. Create manual subscription
        r_create = await ac.post("/api/v1/subscriptions/", json={
            "service_name": "ChatGPT Plus Team",
            "amount": 2500.0,
            "billing_cycle": "monthly",
            "recurring_type": "monthly_subscription"
        }, headers=headers)
        assert r_create.status_code == 200
        assert r_create.json()["service_name"] == "ChatGPT Plus Team"
        created_id = r_create.json()["id"]

        # 6. Delete subscription
        r_del = await ac.delete(f"/api/v1/subscriptions/{created_id}", headers=headers)
        assert r_del.status_code == 200
