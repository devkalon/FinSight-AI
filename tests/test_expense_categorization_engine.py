import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.ml.categorizer import expense_categorizer

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

async def register_and_auth(ac: AsyncClient):
    email = f"catuser_{uuid.uuid4().hex[:8]}@finsight.ai"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Categorizer Tester",
        "preferred_currency": "INR",
        "monthly_income": 80000.0
    }
    res = await ac.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers, res.json()["user_id"]

def test_all_14_required_categories_layer_1():
    test_cases = [
        ("UPI Swiggy Food Delivery", "Food", "Food Delivery"),
        ("Uber City Ride Bangalore", "Transport", "Cabs & Rides"),
        ("Amazon India Online Shopping", "Shopping", "Online Retail"),
        ("Bescom Electricity Monthly Bill", "Bills", "Electricity"),
        ("Netflix Premium 4K Plan", "Subscriptions", "Media Streaming"),
        ("BookMyShow PVR Movie Tickets", "Entertainment", "Movies & Events"),
        ("Udemy Python Programming Course", "Education", "Courses & Books"),
        ("Apollo Pharmacy Medicines", "Healthcare", "Pharmacy & Medicine"),
        ("Monthly House Rent to Landlord", "Rent", "House Rent"),
        ("HDFC Bank Home Loan Monthly EMI", "EMI", "Home Loan"),
        ("Star Health Insurance Annual Premium", "Insurance", "Health Insurance"),
        ("Zerodha Broking Stock Investment", "Investment", "Stocks & Equity"),
        ("IndiGo Airlines Flight to Delhi", "Travel", "Flights & Airlines"),
        ("ATM Cash Withdrawal HDFC Bank", "Other", "Cash Withdrawal")
    ]

    for desc, expected_cat, expected_subcat in test_cases:
        res = expense_categorizer.predict(desc)
        assert res["category"] == expected_cat, f"Failed for '{desc}': got {res['category']}"
        assert res["subcategory"] == expected_subcat
        assert res["classification_method"] in ["deterministic_rule", "ml_classifier"]
        assert res["confidence"] >= 0.70
        assert res["is_low_confidence"] is False

def test_layer_2_ml_classifier_generalization():
    # Phrasing variations without direct merchant names
    res1 = expense_categorizer.predict("Paid fuel charges at station")
    assert res1["category"] == "Transport"
    assert res1["confidence"] >= 0.70

    res2 = expense_categorizer.predict("Supermarket fresh veggies and fruits")
    assert res2["category"] == "Food"

def test_layer_3_llm_fallback_and_low_confidence_flagging():
    # Ambiguous or unknown string should not silently become high-confidence
    res = expense_categorizer.predict("UNKNOWN_VENDOR_TOKEN_9988X")
    assert res["is_low_confidence"] is True
    assert res["confidence"] < 0.70
    assert res["classification_method"] == "llm_fallback"

def test_categorization_evaluation_metrics_benchmark():
    metrics = expense_categorizer.evaluate()
    assert metrics["total_samples"] >= 50
    assert metrics["accuracy"] >= 0.85
    assert metrics["f1_macro"] >= 0.80
    assert metrics["f1_weighted"] >= 0.85
    assert metrics["precision_macro"] >= 0.80
    assert metrics["recall_macro"] >= 0.80
    assert metrics["expected_calibration_error"] <= 0.20
    assert metrics["is_calibrated"] is True

@pytest.mark.asyncio
async def test_layer_4_user_correction_learning_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_and_auth(ac)

        # 1. Fetch categories to get an ID
        cat_res = await ac.get("/api/v1/transactions/categories", headers=headers)
        assert cat_res.status_code == 200
        categories = cat_res.json()
        education_cat = next((c for c in categories if c["name"] == "Education"), categories[0])

        # 2. Before user rule: "Acme Widget Store" would be "Other" or "Shopping"
        res_before = await ac.post("/api/v1/analytics/categorize", json={
            "description": "Acme Widget Custom Vendor"
        }, headers=headers)
        assert res_before.status_code == 200

        # 3. User corrects/learns that "Acme Widget" should be categorized as Education
        learn_payload = {
            "merchant_or_pattern": "acme widget",
            "category_id": education_cat["id"],
            "subcategory": "Specialized Training"
        }
        res_learn = await ac.post("/api/v1/analytics/categories/learn-rule", json=learn_payload, headers=headers)
        assert res_learn.status_code == 200

        # 4. Predict again: Layer 4 must take top priority with confidence 1.0
        res_after = await ac.post("/api/v1/analytics/categorize", json={
            "description": "Payment to Acme Widget Online Portal"
        }, headers=headers)
        assert res_after.status_code == 200
        data_after = res_after.json()
        assert data_after["category"] == education_cat["name"]
        assert data_after["confidence"] == 1.0
        assert data_after["classification_method"] == "user_learned_rule"
        assert data_after["is_low_confidence"] is False

@pytest.mark.asyncio
async def test_categorization_metrics_api_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/v1/analytics/categorization-metrics")
        assert res.status_code == 200
        data = res.json()
        assert "accuracy" in data
        assert "f1_macro" in data
        assert "expected_calibration_error" in data
        assert data["accuracy"] > 0.85
