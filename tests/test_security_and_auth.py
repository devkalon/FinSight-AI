import pytest
import uuid
from datetime import date, timedelta
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.models.transaction import Transaction
from backend.app.models.budget import Budget
from backend.app.models.document import FinancialDocument
from backend.app.core.database import AsyncSessionLocal

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

async def register_and_get_token(ac: AsyncClient, email: str, name: str = "Test User"):
    payload = {
        "email": email,
        "password": "SecurePassword123!",
        "full_name": name,
        "preferred_currency": "INR",
        "monthly_income": 75000.0
    }
    res = await ac.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 200
    data = res.json()
    return data["access_token"], data["user_id"]

@pytest.mark.asyncio
async def test_unauthorized_requests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        endpoints = [
            "/api/v1/auth/me",
            "/api/v1/transactions/",
            "/api/v1/budgets/",
            "/api/v1/goals/",
            "/api/v1/documents/",
            "/api/v1/analytics/health-score"
        ]
        for ep in endpoints:
            res = await ac.get(ep)
            assert res.status_code == 401

@pytest.mark.asyncio
async def test_invalid_and_expired_tokens():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Invalid token
        res_invalid = await ac.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer totally_fake_invalid_token"}
        )
        assert res_invalid.status_code == 401

        # Expired token
        expired_token = create_access_token("fake_user_id", expires_delta=timedelta(minutes=-10))
        res_expired = await ac.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert res_expired.status_code == 401

@pytest.mark.asyncio
async def test_logout_and_token_revocation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"logoutuser_{uuid.uuid4().hex[:8]}@finsight.ai"
        token, user_id = await register_and_get_token(ac, email, "Logout Test")

        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify valid profile access
        res_me = await ac.get("/api/v1/auth/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["email"] == email

        # Logout
        res_logout = await ac.post("/api/v1/auth/logout", headers=headers)
        assert res_logout.status_code == 200

        # Subsequent request with revoked token must fail with 401
        res_revoked = await ac.get("/api/v1/auth/me", headers=headers)
        assert res_revoked.status_code == 401

@pytest.mark.asyncio
async def test_idor_transaction_access_prevention():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create User A & User B
        email_a = f"usera_{uuid.uuid4().hex[:8]}@finsight.ai"
        token_a, user_a_id = await register_and_get_token(ac, email_a, "User A")

        email_b = f"userb_{uuid.uuid4().hex[:8]}@finsight.ai"
        token_b, user_b_id = await register_and_get_token(ac, email_b, "User B")

        # User A creates a transaction
        tx_payload = {
            "amount": 2500.00,
            "transaction_type": "debit",
            "transaction_date": date.today().isoformat(),
            "description": "User A Private Transaction",
            "payment_method": "Credit Card"
        }
        res_create = await ac.post("/api/v1/transactions/", json=tx_payload, headers={"Authorization": f"Bearer {token_a}"})
        assert res_create.status_code == 200
        tx_a_id = res_create.json()["id"]

        # User B attempts to GET User A's transaction -> Must fail with 404
        res_b_get = await ac.get(f"/api/v1/transactions/{tx_a_id}", headers={"Authorization": f"Bearer {token_b}"})
        assert res_b_get.status_code == 404

        # User B attempts to UPDATE User A's transaction -> Must fail with 404
        res_b_update = await ac.put(f"/api/v1/transactions/{tx_a_id}", json={"amount": 9999.0}, headers={"Authorization": f"Bearer {token_b}"})
        assert res_b_update.status_code == 404

        # User B attempts to DELETE User A's transaction -> Must fail with 404
        res_b_del = await ac.delete(f"/api/v1/transactions/{tx_a_id}", headers={"Authorization": f"Bearer {token_b}"})
        assert res_b_del.status_code == 404

@pytest.mark.asyncio
async def test_idor_budget_and_document_prevention():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email_a = f"usera_docs_{uuid.uuid4().hex[:8]}@finsight.ai"
        token_a, user_a_id = await register_and_get_token(ac, email_a, "User A Docs")

        email_b = f"userb_docs_{uuid.uuid4().hex[:8]}@finsight.ai"
        token_b, user_b_id = await register_and_get_token(ac, email_b, "User B Docs")

        # Directly insert a document and budget for User A
        async with AsyncSessionLocal() as db:
            doc = FinancialDocument(
                user_id=user_a_id,
                filename="UserA_Salary_Slip.pdf",
                file_type="salary_slip",
                file_size_bytes=45000,
                storage_path="/uploads/docs/sample.pdf"
            )
            db.add(doc)

            budget = Budget(
                user_id=user_a_id,
                name="User A Private Budget",
                total_limit=Decimal("50000.00"),
                alert_threshold_percentage=85
            )
            db.add(budget)
            await db.commit()
            doc_id = doc.id
            budget_id = budget.id

        # User B attempts to GET User A's Document -> Must fail with 404
        res_doc = await ac.get(f"/api/v1/documents/{doc_id}", headers={"Authorization": f"Bearer {token_b}"})
        assert res_doc.status_code == 404

        # User B attempts to DELETE User A's Document -> Must fail with 404
        res_del_doc = await ac.delete(f"/api/v1/documents/{doc_id}", headers={"Authorization": f"Bearer {token_b}"})
        assert res_del_doc.status_code == 404

        # User B attempts to GET User A's Budget -> Must fail with 404
        res_b_budget = await ac.get(f"/api/v1/budgets/{budget_id}", headers={"Authorization": f"Bearer {token_b}"})
        assert res_b_budget.status_code == 404

        # User B attempts to UPDATE User A's Budget -> Must fail with 404
        res_b_put_budget = await ac.put(f"/api/v1/budgets/{budget_id}", json={"monthly_limit": 1000.0}, headers={"Authorization": f"Bearer {token_b}"})
        assert res_b_put_budget.status_code == 404

@pytest.mark.asyncio
async def test_user_preferences_and_privacy_deletion():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = f"gdpruser_{uuid.uuid4().hex[:8]}@finsight.ai"
        token, user_id = await register_and_get_token(ac, email, "GDPR Test User")
        headers = {"Authorization": f"Bearer {token}"}

        # Update preferences
        pref_payload = {
            "preferred_currency": "USD",
            "preferred_guru": "buffett",
            "risk_tolerance": "aggressive",
            "tax_regime": "old"
        }
        res_pref = await ac.put("/api/v1/auth/me/preferences", json=pref_payload, headers=headers)
        assert res_pref.status_code == 200
        p_data = res_pref.json()
        assert p_data["preferred_currency"] == "USD"
        assert p_data["preferred_guru"] == "buffett"
        assert p_data["risk_tolerance"] == "aggressive"

        # Request Privacy / GDPR Data Deletion
        res_del = await ac.delete("/api/v1/auth/me", headers=headers)
        assert res_del.status_code == 200
        del_data = res_del.json()
        assert del_data["deleted_user_id"] == user_id

        # Verification: Login with deleted user must fail
        login_res = await ac.post("/api/v1/auth/login", json={"email": email, "password": "SecurePassword123!"})
        assert login_res.status_code == 401
