import pytest
import io
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.ai.rag_engine import rag_engine
from backend.app.services.ai.agent import financial_advisor_agent
from backend.app.models.document import FinancialDocument, DocumentChunk
from sqlalchemy.future import select

@pytest.mark.asyncio
async def test_rag_text_extraction_and_cleaning():
    sample_text = """
    # Personal Finance Principles
    
    Chapter 1: The Power of Index Funds.
    Investing systematically in broad-market index funds outperforms 90% of active mutual fund managers over a 15-year horizon.
    Always maintain a 6-month emergency reserve before investing in equities.
    """
    pages = rag_engine.extract_text_from_file(sample_text.encode("utf-8"), "finance_guide.txt")
    assert len(pages) == 1
    assert pages[0]["page_number"] == 1
    assert "index funds" in pages[0]["text"]
    assert "\n\n" not in pages[0]["text"] # Normalized

@pytest.mark.asyncio
async def test_rag_page_aware_chunking():
    pages = [
        {"page_number": 1, "text": "Page 1 intro. Compounding is the eighth wonder of the world. He who understands it, earns it; he who doesn't, pays it."},
        {"page_number": 2, "text": "Page 2 tax planning. Section 80C allows tax deductions up to 1.5 Lakhs in PPF, ELSS, and EPF."}
    ]
    chunks = rag_engine.chunk_document(pages, chunk_size=80, chunk_overlap=20)
    assert len(chunks) >= 2
    assert chunks[0]["page_number"] == 1
    assert chunks[-1]["page_number"] == 2
    assert all(len(c["content"]) >= 20 for c in chunks)

from backend.app.core.database import AsyncSessionLocal
from backend.app.models.user import User

@pytest.mark.asyncio
async def test_rag_database_ingestion_and_user_isolation():
    async with AsyncSessionLocal() as db:
        user_a_id = "user-rag-a-111"
        user_b_id = "user-rag-b-222"

        # Create test users if they don't exist
        for uid, email in [(user_a_id, "usera@rag.ai"), (user_b_id, "userb@rag.ai")]:
            existing = await db.execute(select(User).filter(User.id == uid))
            if not existing.scalars().first():
                user_obj = User(
                    id=uid,
                    email=email,
                    hashed_password="hashed_password_123"
                )
                db.add(user_obj)
        await db.commit()

        guide_content = """
        Comprehensive Real Estate REITs Guide (2026 Edition).
        Commercial REITs in India distribute at least 90% of net taxable cash flows as dividends to unit holders.
        Target dividend yield is typically 6.5% to 8.0% per annum.
        """

        doc_a = await rag_engine.ingest_knowledge_file(
            db=db,
            user_id=user_a_id,
            filename="reit_handbook.txt",
            file_bytes=guide_content.encode("utf-8"),
            source_title="Indian REITs Handbook",
            author="Kalon Wealth Research"
        )

        assert doc_a.file_type == "financial_knowledge"
        assert doc_a.parsed_metadata["source_title"] == "Indian REITs Handbook"

        # User A searches for REITs
        res_a = await rag_engine.retrieve_user_knowledge(
            db=db,
            user_id=user_a_id,
            query="What are Indian REIT dividend yields?",
            top_k=2,
            relevance_threshold=0.15
        )
        assert res_a["answer_supported"] is True
        assert len(res_a["chunks"]) > 0
        top_chunk = res_a["chunks"][0]
        assert "REIT" in top_chunk["relevant_quote"]
        assert top_chunk["source_title"] == "Indian REITs Handbook"
        assert top_chunk["author"] == "Kalon Wealth Research"
        assert top_chunk["page_number"] == 1
        assert top_chunk["relevance_score"] >= 0.15

        # User B searches - must NOT receive User A's custom uploaded chunk
        res_b = await rag_engine.retrieve_user_knowledge(
            db=db,
            user_id=user_b_id,
            query="What are Indian REIT dividend yields?",
            top_k=2,
            relevance_threshold=0.15
        )
        user_b_sources = [c["source_title"] for c in res_b["chunks"]]
        assert "Indian REITs Handbook" not in user_b_sources # Strict user isolation

@pytest.mark.asyncio
async def test_rag_relevance_threshold_and_unsupported_queries():
    async with AsyncSessionLocal() as db:
        res = await rag_engine.retrieve_user_knowledge(
            db=db,
            user_id="any-user-id",
            query="Quantum gravity string theory black hole thermodynamics",
            top_k=3,
            relevance_threshold=0.30
        )
        assert res["answer_supported"] is False
        assert len(res["chunks"]) == 0
        assert "sufficient information" in res["message"]

@pytest.mark.asyncio
async def test_rag_knowledge_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        unique_email = "raguser_api@finsight.ai"
        reg_payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "RAG Testing User",
            "preferred_currency": "INR",
            "monthly_income": 80000.0
        }
        r_reg = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert r_reg.status_code == 200
        token = r_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Upload Knowledge Document
        file_data = b"Sovereign Gold Bonds (SGB) offer 2.5% annual coupon interest plus capital gains tax exemption if held till maturity."
        files = {"file": ("sgb_playbook.txt", io.BytesIO(file_data), "text/plain")}
        data = {"source_title": "SGB Tax Playbook", "author": "Govt Finance"}

        r_up = await ac.post("/api/v1/documents/knowledge/upload", files=files, data=data, headers=headers)
        assert r_up.status_code == 200
        assert r_up.json()["source_title"] == "SGB Tax Playbook"

        # 2. List Knowledge Documents
        r_list = await ac.get("/api/v1/documents/knowledge/list", headers=headers)
        assert r_list.status_code == 200
        docs = r_list.json()
        assert len(docs) >= 1
        assert any(d["source_title"] == "SGB Tax Playbook" for d in docs)

        # 3. Semantic Search Endpoint
        search_payload = {
            "query": "Sovereign Gold Bonds tax exemption",
            "top_k": 2,
            "relevance_threshold": 0.15
        }
        r_search = await ac.post("/api/v1/documents/knowledge/search", json=search_payload, headers=headers)
        assert r_search.status_code == 200
        search_res = r_search.json()
        assert search_res["answer_supported"] is True
        assert len(search_res["chunks"]) > 0
        assert "SGB" in search_res["chunks"][0]["relevant_quote"]

@pytest.mark.asyncio
async def test_advisor_agent_rag_integration():
    async with AsyncSessionLocal() as db:
        res = await financial_advisor_agent.process_query(
            db=db,
            user_id="test_advisor_rag_user",
            user_query="What does Morgan Housel say about compounding and behavior in Psychology of Money?",
            persona="buffett"
        )
        assert "tool_calls" in res
        assert "Psychology of Money" in res["response"]
        assert len(res.get("citations", [])) > 0
        citation = res["citations"][0]
        assert "Psychology of Money" in citation["source_title"]
        assert citation["relevance_score"] > 0
