import pytest
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.ml.anomaly_detector import anomaly_detector

def test_category_spending_surge_detection():
    # Synthetic transactions: Food typical ~₹6,200/mo, current surges to ₹15,800
    transactions = [
        # Month 1 Food
        {"id": "f1", "transaction_type": "debit", "category_name": "Food", "amount": 2000.0, "transaction_date": "2026-06-10", "merchant": "Supermarket"},
        {"id": "f2", "transaction_type": "debit", "category_name": "Food", "amount": 2200.0, "transaction_date": "2026-06-20", "merchant": "Grocery Hub"},
        {"id": "f3", "transaction_type": "debit", "category_name": "Food", "amount": 2000.0, "transaction_date": "2026-06-28", "merchant": "Swiggy"},
        # Month 2 Food
        {"id": "f4", "transaction_type": "debit", "category_name": "Food", "amount": 3000.0, "transaction_date": "2026-07-05", "merchant": "Supermarket"},
        {"id": "f5", "transaction_type": "debit", "category_name": "Food", "amount": 3200.0, "transaction_date": "2026-07-18", "merchant": "Dining Out"},
        # Month 3 (Current) Food surge: ₹15,800
        {"id": "f6", "transaction_type": "debit", "category_name": "Food", "amount": 8000.0, "transaction_date": "2026-08-05", "merchant": "Luxury Dining"},
        {"id": "f7", "transaction_type": "debit", "category_name": "Food", "amount": 7800.0, "transaction_date": "2026-08-20", "merchant": "Gourmet Import"}
    ]

    res = anomaly_detector.detect_detailed_anomalies(transactions, currency="INR")
    assert res["has_sufficient_history"] is True
    assert res["total_anomalies"] >= 1

    cat_anoms = [a for a in res["anomalies"] if a["anomaly_type"] == "category_spending" and a["entity_name"] == "Food"]
    assert len(cat_anoms) == 1
    anom = cat_anoms[0]
    assert anom["observed_value"] == 15800.0
    assert anom["expected_value"] <= 6500.0
    assert anom["deviation_pct"] >= 100.0
    assert "Food spending reached INR 15,800.00" in anom["explanation"] or "Food" in anom["explanation"]
    assert len(anom["affected_transactions"]) >= 2

def test_transaction_amount_outlier_zscore():
    # Normal spending between ₹800 and ₹2,500, with one massive ₹48,000 outlier
    transactions = [
        {"id": f"t_{i}", "transaction_type": "debit", "category_name": "General", "amount": float(1000 + (i * 150)), "transaction_date": "2026-08-01", "merchant": "Retail Store"}
        for i in range(10)
    ]
    transactions.append({
        "id": "outlier_1",
        "transaction_type": "debit",
        "category_name": "Shopping",
        "amount": 48000.0,
        "transaction_date": "2026-08-15",
        "merchant": "Apple Store"
    })

    res = anomaly_detector.detect_detailed_anomalies(transactions, currency="INR")
    outliers = [a for a in res["anomalies"] if a["anomaly_type"] == "transaction_amount"]
    assert len(outliers) >= 1
    outlier = outliers[0]
    assert outlier["observed_value"] == 48000.0
    assert outlier["severity"] in ["high", "critical"]
    assert "Apple Store" in outlier["explanation"]

def test_merchant_spending_surge():
    transactions = [
        {"id": "m1", "transaction_type": "debit", "merchant": "Amazon", "amount": 1200.0, "transaction_date": "2026-06-01"},
        {"id": "m2", "transaction_type": "debit", "merchant": "Amazon", "amount": 1500.0, "transaction_date": "2026-07-01"},
        {"id": "m3", "transaction_type": "debit", "merchant": "Amazon", "amount": 1800.0, "transaction_date": "2026-07-15"},
        {"id": "m4", "transaction_type": "debit", "merchant": "Amazon", "amount": 18500.0, "transaction_date": "2026-08-20"} # 10x spike
    ]

    res = anomaly_detector.detect_detailed_anomalies(transactions, currency="INR")
    merchant_anoms = [a for a in res["anomalies"] if a["anomaly_type"] == "merchant_spending" and a["entity_name"] == "Amazon"]
    assert len(merchant_anoms) == 1
    assert merchant_anoms[0]["observed_value"] == 18500.0
    assert merchant_anoms[0]["deviation_pct"] >= 200.0

def test_frequency_burst_spike():
    # 7 transactions on the same day vs 1 per day on previous days
    transactions = [
        {"id": "d1", "transaction_type": "debit", "amount": 200.0, "transaction_date": "2026-08-01"},
        {"id": "d2", "transaction_type": "debit", "amount": 300.0, "transaction_date": "2026-08-02"},
        {"id": "d3", "transaction_type": "debit", "amount": 250.0, "transaction_date": "2026-08-03"},
    ]
    for i in range(7):
        transactions.append({
            "id": f"burst_{i}",
            "transaction_type": "debit",
            "amount": 150.0,
            "transaction_date": "2026-08-04"
        })

    res = anomaly_detector.detect_detailed_anomalies(transactions, currency="INR")
    freq_anoms = [a for a in res["anomalies"] if a["anomaly_type"] == "frequency_spike"]
    assert len(freq_anoms) >= 1
    assert freq_anoms[0]["observed_value"] == 7.0

def test_recurring_subscription_price_hike():
    transactions = [
        {"id": "n1", "transaction_type": "debit", "description": "Netflix Monthly", "amount": 499.0, "transaction_date": "2026-06-15"},
        {"id": "n2", "transaction_type": "debit", "description": "Netflix Monthly", "amount": 499.0, "transaction_date": "2026-07-15"},
        {"id": "n3", "transaction_type": "debit", "description": "Netflix Monthly", "amount": 649.0, "transaction_date": "2026-08-15"}
    ]

    res = anomaly_detector.detect_detailed_anomalies(transactions, currency="INR")
    rec_anoms = [a for a in res["anomalies"] if a["anomaly_type"] == "recurring_change"]
    assert len(rec_anoms) == 1
    assert rec_anoms[0]["observed_value"] == 649.0
    assert rec_anoms[0]["expected_value"] == 499.0
    assert rec_anoms[0]["deviation_pct"] == 30.1

def test_false_positive_guardrail_insufficient_history():
    # Only 1 transaction: should gracefully report insufficient history without throwing or creating false positives
    transactions = [
        {"id": "single", "transaction_type": "debit", "category_name": "Food", "amount": 50000.0, "transaction_date": "2026-08-01"}
    ]

    res = anomaly_detector.detect_detailed_anomalies(transactions, currency="INR")
    assert res["has_sufficient_history"] is False
    assert res["total_anomalies"] == 0
    assert "Insufficient" in res["message"]

@pytest.mark.asyncio
async def test_anomalies_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = "anomaly_user@finsight.ai"
        r_reg = await ac.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "full_name": "Anomaly Tester",
            "preferred_currency": "INR",
            "monthly_income": 100000.0
        })
        assert r_reg.status_code == 200
        token = r_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create transactions with an anomaly
        for i in range(5):
            await ac.post("/api/v1/transactions/", json={
                "amount": 1000.0 + (i * 200),
                "transaction_type": "debit",
                "transaction_date": f"2026-08-0{i+1}",
                "description": f"Standard Purchase {i}",
                "merchant_name": "Store"
            }, headers=headers)

        # Huge outlier
        await ac.post("/api/v1/transactions/", json={
            "amount": 75000.0,
            "transaction_type": "debit",
            "transaction_date": "2026-08-10",
            "description": "High value jewelry purchase",
            "merchant_name": "Tanishq"
        }, headers=headers)

        # 1. GET /api/v1/analytics/anomalies
        r_anom = await ac.get("/api/v1/analytics/anomalies", headers=headers)
        assert r_anom.status_code == 200
        anom_data = r_anom.json()
        assert "total_anomalies" in anom_data
        assert anom_data["total_anomalies"] >= 1
        assert anom_data["has_sufficient_history"] is True

        # 2. POST /api/v1/analytics/anomalies/scan
        r_scan = await ac.post("/api/v1/analytics/anomalies/scan", headers=headers)
        assert r_scan.status_code == 200
        assert r_scan.json()["total_anomalies"] >= 1
