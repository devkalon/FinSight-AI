import pytest
import uuid
import os
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import AsyncSessionLocal, init_db

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

@pytest.mark.asyncio
async def test_e2e_complete_10_step_user_workflow():
    """
    Complete 10-Step E2E Integration Workflow:
    1. Register
    2. Login
    3. Upload Transaction Statement
    4. Verify OCR / Candidate Extraction Result
    5. Categorize & Confirm Candidate Transactions to Ledger
    6. View Dashboard & Financial Health Score
    7. Create Category Budget
    8. Create Financial Goal
    9. Ask AI Advisor
    10. Generate Monthly Report & PDF
    """
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # STEP 1: REGISTER
        test_email = f"e2e_user_{uuid.uuid4().hex[:8]}@finsight.ai"
        test_password = "SecurePassword123!"
        
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": test_email,
            "password": test_password,
            "full_name": "E2E Test User"
        })
        assert reg_res.status_code == 200, f"Register failed: {reg_res.text}"
        reg_data = reg_res.json()
        assert "access_token" in reg_data

        # STEP 2: LOGIN
        login_res = await client.post("/api/v1/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # STEP 3: UPLOAD TRANSACTION STATEMENT (CSV)
        csv_content = (
            "Date,Description,Amount,Type,Category,Merchant\n"
            f"{date.today() - timedelta(days=5)},Salary Credit,75000.00,credit,Income,TechCorp\n"
            f"{date.today() - timedelta(days=3)},Groceries at Reliance Smart,4200.00,debit,Groceries,Reliance Smart\n"
            f"{date.today() - timedelta(days=1)},Uber Ride to Airport,850.00,debit,Transport,Uber\n"
        ).encode("utf-8")

        files = {"file": ("statement.csv", csv_content, "text/csv")}
        upload_res = await client.post("/api/v1/documents/upload/bank-statement", headers=headers, files=files)
        assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
        doc_data = upload_res.json()
        doc_id = doc_data["document_id"]
        assert (doc_data.get("total_extracted_transactions") or doc_data.get("total_parsed_transactions", 0)) >= 3

        # STEP 4: VERIFY OCR / CANDIDATE EXTRACTION RESULT
        candidates = doc_data["candidates"]
        assert len(candidates) >= 3
        grocery_cand = next(c for c in candidates if "Reliance" in c["description"] or "Groceries" in c.get("suggested_category", ""))
        assert grocery_cand["amount"] == 4200.0

        # STEP 5: CATEGORIZE & CONFIRM CANDIDATES TO LEDGER
        confirm_res = await client.post(f"/api/v1/documents/{doc_id}/confirm", headers=headers, json={
            "transactions": [
                {
                    "description": "Monthly Salary",
                    "amount": 75000.0,
                    "transaction_type": "credit",
                    "transaction_date": str(date.today() - timedelta(days=5)),
                    "category_suggestion": "Income",
                    "merchant_name": "TechCorp"
                },
                {
                    "description": "Groceries at Reliance Smart",
                    "amount": 4200.0,
                    "transaction_type": "debit",
                    "transaction_date": str(date.today() - timedelta(days=3)),
                    "category_suggestion": "Groceries",
                    "merchant_name": "Reliance Smart"
                },
                {
                    "description": "Uber Ride to Airport",
                    "amount": 850.0,
                    "transaction_type": "debit",
                    "transaction_date": str(date.today() - timedelta(days=1)),
                    "category_suggestion": "Transport",
                    "merchant_name": "Uber"
                }
            ]
        })
        assert confirm_res.status_code == 200, f"Confirm failed: {confirm_res.text}"
        assert confirm_res.json()["committed_count"] == 3

        # STEP 6: VIEW DASHBOARD & FINANCIAL HEALTH SCORE
        health_res = await client.get("/api/v1/analytics/health-score", headers=headers)
        assert health_res.status_code == 200
        health_data = health_res.json()
        assert "score" in health_data
        assert health_data["score"] > 0

        # STEP 7: CREATE BUDGET
        budget_res = await client.post("/api/v1/budgets/", headers=headers, json={
            "category_name": "Groceries",
            "monthly_limit": 10000.0,
            "warning_threshold_pct": 80.0
        })
        assert budget_res.status_code == 200
        assert budget_res.json()["monthly_limit"] == 10000.0

        # STEP 8: CREATE GOAL
        goal_res = await client.post("/api/v1/goals/", headers=headers, json={
            "title": "Emergency Fund",
            "target_amount": 150000.0,
            "current_amount": 30000.0,
            "target_date": "2027-12-31",
            "monthly_contribution": 10000.0
        })
        assert goal_res.status_code == 200
        assert goal_res.json()["target_amount"] == 150000.0

        # STEP 9: ASK AI ADVISOR
        advisor_res = await client.post("/api/v1/advisor/chat", headers=headers, json={
            "message": "What is my current monthly income and total expenses?"
        })
        assert advisor_res.status_code == 200
        adv_data = advisor_res.json()
        assert "response" in adv_data or "content" in adv_data
        text = adv_data.get("response") or adv_data.get("content", "")
        assert len(text) > 0

        # STEP 10: GENERATE MONTHLY REPORT & PDF
        report_res = await client.get("/api/v1/reports/monthly", headers=headers)
        assert report_res.status_code == 200
        report_data = report_res.json()
        assert "executive_summary" in report_data.get("narrative", {}) or "executive_summary" in report_data
        assert "narrative" in report_data

        pdf_res = await client.get(f"/api/v1/reports/monthly/pdf?token={token}", headers=headers)
        assert pdf_res.status_code == 200
        assert pdf_res.headers.get("content-type") == "application/pdf"
        assert len(pdf_res.content) > 500
