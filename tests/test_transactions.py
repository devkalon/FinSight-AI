import pytest
import uuid
from datetime import date, timedelta
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

async def register_user_and_auth(ac: AsyncClient):
    email = f"txuser_{uuid.uuid4().hex[:8]}@finsight.ai"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Tx Test User",
        "preferred_currency": "INR",
        "monthly_income": 80000.0
    }
    res = await ac.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers, res.json()["user_id"]

@pytest.mark.asyncio
async def test_transaction_crud_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_user_and_auth(ac)

        # 1. Create Transaction with full fields
        create_payload = {
            "amount": 3450.75,
            "currency": "INR",
            "transaction_type": "debit",
            "transaction_date": date.today().isoformat(),
            "description": "Premium Dinner at Barbeque Nation",
            "merchant_name": "Barbeque Nation",
            "subcategory": "Fine Dining",
            "payment_method": "Credit Card",
            "source": "manual",
            "confidence_score": 1.0,
            "notes": "Team quarterly celebration dinner",
            "extra_metadata": '{"table": 12, "voucher_applied": true}'
        }
        res_create = await ac.post("/api/v1/transactions/", json=create_payload, headers=headers)
        assert res_create.status_code == 200
        tx_data = res_create.json()
        tx_id = tx_data["id"]

        assert tx_data["amount"] == 3450.75
        assert tx_data["currency"] == "INR"
        assert tx_data["merchant_name"] == "Barbeque Nation"
        assert tx_data["subcategory"] == "Fine Dining"
        assert tx_data["payment_method"] == "Credit Card"
        assert tx_data["notes"] == "Team quarterly celebration dinner"
        assert tx_data["extra_metadata"] == '{"table": 12, "voucher_applied": true}'

        # 2. View Transaction Details (GET /{id})
        res_get = await ac.get(f"/api/v1/transactions/{tx_id}", headers=headers)
        assert res_get.status_code == 200
        detail = res_get.json()
        assert detail["id"] == tx_id
        assert detail["description"] == "Premium Dinner at Barbeque Nation"

        # 3. Edit / Update Transaction (PUT /{id})
        update_payload = {
            "amount": 3890.00,
            "notes": "Updated team dinner with dessert added",
            "subcategory": "Buffet & Bar"
        }
        res_put = await ac.put(f"/api/v1/transactions/{tx_id}", json=update_payload, headers=headers)
        assert res_put.status_code == 200
        updated = res_put.json()
        assert updated["amount"] == 3890.00
        assert updated["notes"] == "Updated team dinner with dessert added"
        assert updated["subcategory"] == "Buffet & Bar"

        # 4. Delete Transaction (DELETE /{id})
        res_del = await ac.delete(f"/api/v1/transactions/{tx_id}", headers=headers)
        assert res_del.status_code == 200

        # Verification: GET deleted transaction must return 404
        res_after_del = await ac.get(f"/api/v1/transactions/{tx_id}", headers=headers)
        assert res_after_del.status_code == 404

@pytest.mark.asyncio
async def test_transaction_search_and_multi_filtering():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_user_and_auth(ac)

        # Seed 4 diverse transactions
        today = date.today()
        txs = [
            {
                "amount": 550.0,
                "transaction_type": "debit",
                "transaction_date": (today - timedelta(days=5)).isoformat(),
                "description": "Starbucks Caramel Frappuccino",
                "merchant_name": "Starbucks Coffee",
                "payment_method": "UPI",
                "source": "manual",
                "notes": "Coffee with colleague"
            },
            {
                "amount": 4200.0,
                "transaction_type": "debit",
                "transaction_date": (today - timedelta(days=2)).isoformat(),
                "description": "Amazon Purchase - Wireless Earbuds",
                "merchant_name": "Amazon",
                "payment_method": "Credit Card",
                "source": "manual",
                "notes": "Electronics gadget"
            },
            {
                "amount": 120000.0,
                "transaction_type": "credit",
                "transaction_date": today.isoformat(),
                "description": "Salary Deposit for August",
                "merchant_name": "Acme Corp",
                "payment_method": "Net Banking",
                "source": "bank_pdf",
                "notes": "Direct payroll credit"
            },
            {
                "amount": 1200.0,
                "transaction_type": "debit",
                "transaction_date": today.isoformat(),
                "description": "Uber Premier Airport Ride",
                "merchant_name": "Uber",
                "payment_method": "UPI",
                "source": "ocr_receipt",
                "notes": "Travel to terminal"
            }
        ]

        for item in txs:
            r = await ac.post("/api/v1/transactions/", json=item, headers=headers)
            assert r.status_code == 200

        # Test Search Keyword (Description & Merchant & Notes)
        res_search = await ac.get("/api/v1/transactions/?search=Starbucks", headers=headers)
        assert res_search.status_code == 200
        data = res_search.json()
        assert data["total_count"] == 1
        assert "Starbucks" in data["items"][0]["description"]

        # Test Filter by Transaction Type (Credit)
        res_type = await ac.get("/api/v1/transactions/?transaction_type=credit", headers=headers)
        assert res_type.status_code == 200
        assert res_type.json()["total_count"] == 1
        assert res_type.json()["items"][0]["amount"] == 120000.0

        # Test Filter by Payment Method (UPI)
        res_upi = await ac.get("/api/v1/transactions/?payment_method=UPI", headers=headers)
        assert res_upi.status_code == 200
        assert res_upi.json()["total_count"] == 2

        # Test Filter by Amount Range (min_amount=1000, max_amount=5000)
        res_amt = await ac.get("/api/v1/transactions/?min_amount=1000&max_amount=5000", headers=headers)
        assert res_amt.status_code == 200
        assert res_amt.json()["total_count"] == 2 # Amazon (4200) and Uber (1200)

        # Test Filter by Date Range (past 3 days)
        start_d = (today - timedelta(days=3)).isoformat()
        res_date = await ac.get(f"/api/v1/transactions/?start_date={start_d}", headers=headers)
        assert res_date.status_code == 200
        assert res_date.json()["total_count"] == 3

@pytest.mark.asyncio
async def test_transaction_sorting_and_pagination():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_user_and_auth(ac)

        today = date.today()
        # Create 5 distinct transactions
        amounts = [100.0, 500.0, 250.0, 1000.0, 750.0]
        for i, amt in enumerate(amounts):
            payload = {
                "amount": amt,
                "transaction_type": "debit",
                "transaction_date": (today - timedelta(days=i)).isoformat(),
                "description": f"Tx Item #{i+1}",
                "payment_method": "UPI"
            }
            await ac.post("/api/v1/transactions/", json=payload, headers=headers)

        # Sort by Amount Descending
        res_sort_amt_desc = await ac.get("/api/v1/transactions/?sort_by=amount&sort_order=desc", headers=headers)
        assert res_sort_amt_desc.status_code == 200
        items = res_sort_amt_desc.json()["items"]
        assert items[0]["amount"] == 1000.0
        assert items[-1]["amount"] == 100.0

        # Sort by Amount Ascending
        res_sort_amt_asc = await ac.get("/api/v1/transactions/?sort_by=amount&sort_order=asc", headers=headers)
        assert res_sort_amt_asc.status_code == 200
        items_asc = res_sort_amt_asc.json()["items"]
        assert items_asc[0]["amount"] == 100.0
        assert items_asc[-1]["amount"] == 1000.0

        # Pagination Page 1 with page_size=2
        res_p1 = await ac.get("/api/v1/transactions/?page=1&page_size=2&sort_by=amount&sort_order=desc", headers=headers)
        assert res_p1.status_code == 200
        p1_data = res_p1.json()
        assert p1_data["page"] == 1
        assert p1_data["page_size"] == 2
        assert p1_data["total_count"] == 5
        assert p1_data["total_pages"] == 3
        assert len(p1_data["items"]) == 2
        assert p1_data["items"][0]["amount"] == 1000.0
        assert p1_data["items"][1]["amount"] == 750.0

        # Pagination Page 2 with page_size=2
        res_p2 = await ac.get("/api/v1/transactions/?page=2&page_size=2&sort_by=amount&sort_order=desc", headers=headers)
        assert res_p2.status_code == 200
        p2_data = res_p2.json()
        assert p2_data["page"] == 2
        assert len(p2_data["items"]) == 2
        assert p2_data["items"][0]["amount"] == 500.0
        assert p2_data["items"][1]["amount"] == 250.0
