import os
import io
import pytest
import uuid
from datetime import date
from httpx import AsyncClient, ASGITransport
import pandas as pd
from backend.app.main import app
from backend.app.services.ingestion.indian_normalization import indian_normalizer
from backend.app.services.ingestion.adapters.adapter_registry import adapter_registry
from backend.app.services.ingestion.adapters.base_adapter import BankStatementAdapter
from backend.app.services.ingestion.adapters.hdfc_adapter import HDFCBankAdapter
from backend.app.services.ingestion.adapters.sbi_adapter import SBIBankAdapter
from backend.app.services.ingestion.adapters.upi_adapter import UPIExportAdapter

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

async def register_and_auth(ac: AsyncClient):
    email = f"indian_user_{uuid.uuid4().hex[:8]}@finsight.ai"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Indian Financial Tester",
        "preferred_currency": "INR",
        "monthly_income": 85000.0
    }
    res = await ac.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers, res.json()["user_id"]

def test_indian_amount_normalization():
    assert indian_normalizer.parse_indian_amount("1,50,000.00") == 150000.0
    assert indian_normalizer.parse_indian_amount("₹ 12,34,567.89") == 1234567.89
    assert indian_normalizer.parse_indian_amount("Rs. 450/-") == 450.0
    assert indian_normalizer.parse_indian_amount("1,250.50 Cr") == 1250.50
    assert indian_normalizer.parse_indian_amount("INR 99,000") == 99000.0
    assert indian_normalizer.parse_indian_amount("- 320.00") == 320.0
    assert indian_normalizer.parse_indian_amount(None) == 0.0

def test_indian_date_normalization():
    assert indian_normalizer.parse_indian_date("15/08/2026") == date(2026, 8, 15)
    assert indian_normalizer.parse_indian_date("01-Aug-2026") == date(2026, 8, 1)
    assert indian_normalizer.parse_indian_date("25-08-26") == date(2026, 8, 25)
    assert indian_normalizer.parse_indian_date("2026-08-10") == date(2026, 8, 10)

def test_indian_merchant_and_upi_extraction():
    # 1. UPI Transfer
    m1, sub1, utr1 = indian_normalizer.extract_indian_merchant("UPI-SWIGGY-swiggy@icici-902183129012")
    assert "Swiggy" in m1
    assert utr1 == "902183129012"

    # 2. POS Card swipe
    m2, sub2, _ = indian_normalizer.extract_indian_merchant("POS 401234XXXXXX1234 STARBUCKS BANGALORE IN")
    assert "Starbucks" in m2

    # 3. NEFT Salary credit
    m3, sub3, _ = indian_normalizer.extract_indian_merchant("NEFT CR-N12345678-TECH CORP-SALARY AUGUST 2026")
    assert "Tech Corp" in m3

    # 4. ACH Mutual fund SIP
    m4, sub4, _ = indian_normalizer.extract_indian_merchant("ACH D- HDFC MUTUAL FUND SIP-901283")
    assert "Hdfc Mutual" in m4

    # 5. Utility bill
    m5, sub5, _ = indian_normalizer.extract_indian_merchant("BILLPAY-BESCOM-BLR-01293")
    assert "Bescom" in m5

def test_statement_integrity_balance_validation():
    txs = [
        {"amount": 1000.0, "transaction_type": "debit"},
        {"amount": 2500.0, "transaction_type": "debit"},
        {"amount": 50000.0, "transaction_type": "credit"}
    ]
    # Opening 10000 + Credits 50000 - Debits 3500 = 56500
    res_balanced = indian_normalizer.validate_statement_integrity(10000.0, 56500.0, txs)
    assert res_balanced["is_balanced"] is True
    assert res_balanced["total_debits"] == 3500.0
    assert res_balanced["total_credits"] == 50000.0

    # Imbalanced
    res_imbalanced = indian_normalizer.validate_statement_integrity(10000.0, 50000.0, txs)
    assert res_imbalanced["is_balanced"] is False
    assert res_imbalanced["balance_discrepancy"] == 6500.0

@pytest.mark.asyncio
async def test_hdfc_sample_statement_ingestion():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_and_auth(ac)

        sample_path = os.path.join("data", "sample_statements", "sample_hdfc_statement.csv")
        with open(sample_path, "rb") as f:
            content = f.read()

        files = {"file": ("hdfc_aug_2026.csv", content, "text/csv")}
        res = await ac.post("/api/v1/documents/upload/bank-statement", files=files, headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["total_parsed_transactions"] >= 7
        assert data["account_summary"]["bank_code"] == "hdfc"
        assert data["account_summary"]["is_balanced"] is True

        # Check extracted merchants
        merchants = [c["merchant_name"] for c in data["candidates"]]
        assert any("Swiggy" in m for m in merchants)
        assert any("Starbucks" in m for m in merchants)
        assert any("Blinkit" in m for m in merchants)

@pytest.mark.asyncio
async def test_sbi_sample_statement_ingestion():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_and_auth(ac)

        sample_path = os.path.join("data", "sample_statements", "sample_sbi_statement.csv")
        with open(sample_path, "rb") as f:
            content = f.read()

        files = {"file": ("sbi_savings_statement.csv", content, "text/csv")}
        res = await ac.post("/api/v1/documents/upload/bank-statement", files=files, headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["total_parsed_transactions"] >= 5
        assert data["account_summary"]["bank_code"] == "sbi"

@pytest.mark.asyncio
async def test_phonepe_upi_export_ingestion():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_and_auth(ac)

        sample_path = os.path.join("data", "sample_statements", "sample_phonepe_upi_export.csv")
        with open(sample_path, "rb") as f:
            content = f.read()

        files = {"file": ("phonepe_statement_2026.csv", content, "text/csv")}
        res = await ac.post("/api/v1/documents/upload/bank-statement", files=files, headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert data["total_parsed_transactions"] >= 5
        assert data["account_summary"]["bank_code"] == "upi_export"

@pytest.mark.asyncio
async def test_duplicate_detection_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_and_auth(ac)

        # 1. First upload & confirm HDFC statement
        sample_path = os.path.join("data", "sample_statements", "sample_hdfc_statement.csv")
        with open(sample_path, "rb") as f:
            content = f.read()

        files = {"file": ("hdfc_first_upload.csv", content, "text/csv")}
        res1 = await ac.post("/api/v1/documents/upload/bank-statement", files=files, headers=headers)
        assert res1.status_code == 200
        doc1_id = res1.json()["document_id"]
        cands1 = res1.json()["candidates"]

        # Confirm transactions into ledger
        await ac.post(f"/api/v1/documents/{doc1_id}/confirm", json={"transactions": cands1}, headers=headers)

        # 2. Re-upload identical file to test duplicate detection
        files2 = {"file": ("hdfc_duplicate_upload.csv", content, "text/csv")}
        res2 = await ac.post("/api/v1/documents/upload/bank-statement", files=files2, headers=headers)
        assert res2.status_code == 200
        cands2 = res2.json()["candidates"]

        # All candidates must now be marked is_duplicate == True
        duplicate_flags = [c.get("is_duplicate", False) for c in cands2]
        assert all(duplicate_flags)
        assert "Potential duplicate" in cands2[0]["duplicate_reason"]

def test_dynamic_custom_bank_adapter_registration():
    class KotakMahindraAdapter(BankStatementAdapter):
        @property
        def name(self) -> str:
            return "Kotak Mahindra Bank Adapter"
        @property
        def bank_code(self) -> str:
            return "kotak"
        def matches_format(self, columns, sample_text=""):
            return any("kotak" in c.lower() for c in columns) or "kotak" in sample_text.lower()
        def parse_dataframe(self, df: pd.DataFrame):
            return [{"id": "k1", "amount": 999.0, "description": "Kotak NetBanking"}], {"bank_code": "kotak"}

    kotak_adapter = KotakMahindraAdapter()
    adapter_registry.register_adapter(kotak_adapter, prepend=True)

    detected = adapter_registry.detect_adapter(["sl no", "kotak transaction date", "amount"])
    assert detected.bank_code == "kotak"
    assert detected.name == "Kotak Mahindra Bank Adapter"
