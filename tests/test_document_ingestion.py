import io
import pytest
import uuid
from PIL import Image
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.ingestion.preprocessing import image_preprocessor
from backend.app.services.ingestion.ocr_provider import (
    OCRProviderInterface, OCRManager, ocr_manager, PatternHeuristicOCRProvider
)

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

async def register_and_auth(ac: AsyncClient):
    email = f"docuser_{uuid.uuid4().hex[:8]}@finsight.ai"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Doc Ingestion Tester",
        "preferred_currency": "INR",
        "monthly_income": 75000.0
    }
    res = await ac.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers, res.json()["user_id"]

def create_dummy_receipt_image() -> bytes:
    img = Image.new("RGB", (600, 800), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def create_dummy_csv_statement() -> bytes:
    csv_content = """Date,Description,Debit,Credit,Balance
2026-08-20,SWIGGY ONLINE ORDER,450.00,,45000.00
2026-08-22,TECH CORP MONTHLY PAYROLL,,85000.00,130000.00
2026-08-25,AMAZON RETAIL PURCHASE,2199.00,,127801.00
2026-08-26,HDFC MUTUAL FUND SIP,5000.00,,122801.00
"""
    return csv_content.encode("utf-8")

def test_image_preprocessor():
    # Test image preprocessing with different dimensions
    raw_img = Image.new("RGBA", (400, 300), color=(200, 200, 200, 255))
    processed = image_preprocessor.preprocess(raw_img)
    assert processed.mode == "L" # Converted to Grayscale
    assert processed.size[0] >= 1000 # Upscaled for optimal OCR resolution

def test_ocr_provider_abstraction_and_custom_swap():
    class MockCustomOCRProvider(OCRProviderInterface):
        @property
        def name(self) -> str:
            return "Mock-Custom-Provider"
        
        def is_available(self) -> bool:
            return True
        
        def extract_text(self, image: Image.Image, context=None):
            return "MOCK OCR TEXT: STARBUCKS TOTAL PAID INR 450.00", 0.99, self.name

    test_manager = OCRManager()
    custom_prov = MockCustomOCRProvider()
    test_manager.set_primary_provider(custom_prov)

    img = Image.new("RGB", (100, 100))
    text, conf, name = test_manager.extract(img)
    assert name == "Mock-Custom-Provider"
    assert "STARBUCKS" in text
    assert conf == 0.99

@pytest.mark.asyncio
async def test_receipt_ocr_upload_and_candidate_generation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_and_auth(ac)

        img_bytes = create_dummy_receipt_image()
        files = {"file": ("swiggy_food_receipt.png", img_bytes, "image/png")}

        res = await ac.post("/api/v1/documents/upload/receipt", files=files, headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert "document_id" in data
        assert data["filename"] == "swiggy_food_receipt.png"
        assert "candidates" in data
        assert len(data["candidates"]) >= 1

        cand = data["candidates"][0]
        assert cand["amount"] > 0
        assert cand["confidence_score"] > 0.60
        assert "Swiggy" in cand["merchant_name"] or "Food" in cand["category_suggestion"]

@pytest.mark.asyncio
async def test_bank_statement_csv_upload():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_and_auth(ac)

        csv_bytes = create_dummy_csv_statement()
        files = {"file": ("hdfc_statement.csv", csv_bytes, "text/csv")}

        res = await ac.post("/api/v1/documents/upload/bank-statement", files=files, headers=headers)
        assert res.status_code == 200
        data = res.json()

        assert "document_id" in data
        assert data["total_parsed_transactions"] >= 4
        assert len(data["candidates"]) >= 4

        # Check that credit and debit transactions were correctly classified
        types = [c["transaction_type"] for c in data["candidates"]]
        assert "credit" in types
        assert "debit" in types

@pytest.mark.asyncio
async def test_candidate_confirmation_and_ledger_commit():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_and_auth(ac)

        # 1. Upload receipt
        img_bytes = create_dummy_receipt_image()
        files = {"file": ("starbucks_coffee_receipt.png", img_bytes, "image/png")}
        res_upload = await ac.post("/api/v1/documents/upload/receipt", files=files, headers=headers)
        assert res_upload.status_code == 200
        doc_id = res_upload.json()["document_id"]
        candidates = res_upload.json()["candidates"]

        # Edit candidate values manually (Simulating user review)
        candidates[0]["amount"] = 520.0
        candidates[0]["merchant_name"] = "Starbucks Reserve"
        candidates[0]["description"] = "Coffee & Bakery with Client"

        # 2. Confirm candidate transactions
        confirm_payload = {"transactions": candidates}
        res_confirm = await ac.post(f"/api/v1/documents/{doc_id}/confirm", json=confirm_payload, headers=headers)
        assert res_confirm.status_code == 200
        confirm_data = res_confirm.json()
        assert confirm_data["committed_count"] == len(candidates)
        assert len(confirm_data["transaction_ids"]) == len(candidates)

        # 3. Verify that transactions now exist in the user's primary transactions ledger
        res_txs = await ac.get("/api/v1/transactions/?search=Starbucks", headers=headers)
        assert res_txs.status_code == 200
        txs_data = res_txs.json()
        assert txs_data["total_count"] >= 1
        assert txs_data["items"][0]["amount"] == 520.0
        assert txs_data["items"][0]["merchant_name"] == "Starbucks Reserve"

        # 4. Verify Document Status is updated to confirmed
        res_doc = await ac.get(f"/api/v1/documents/{doc_id}", headers=headers)
        assert res_doc.status_code == 200
        assert res_doc.json()["processing_status"] == "confirmed"

@pytest.mark.asyncio
async def test_file_validation_security():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers, user_id = await register_and_auth(ac)

        # Disallow executable / unsafe files
        unsafe_file = {"file": ("malicious_script.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload")}
        res_unsafe = await ac.post("/api/v1/documents/upload/receipt", files=unsafe_file, headers=headers)
        assert res_unsafe.status_code == 400
