import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.ai.gurus import philosophy_engine, guru_engine

def test_philosophy_dimension_classification():
    assert philosophy_engine.detect_dimension("Should I prepay my 9% home loan or invest in SIP?") == "debt"
    assert philosophy_engine.detect_dimension("Should I invest in Nifty 50 or REITs?") == "investing"
    assert philosophy_engine.detect_dimension("How do I split my income in 50/30/20 budget?") == "budgeting"
    assert philosophy_engine.detect_dimension("How much should I keep in liquid emergency fund?") == "saving"
    assert philosophy_engine.detect_dimension("Is buying an expensive luxury sports car worth it?") == "lifestyle_spending"
    assert philosophy_engine.detect_dimension("How to plan for early retirement FIRE target?") == "financial_goals"

def test_structured_philosophy_profiles_metadata():
    philosophies = philosophy_engine.list_philosophies()
    assert len(philosophies) >= 4
    for p in philosophies:
        assert "documented_foundation" in p
        assert "core_axiom" in p
        assert "dimensions" in p
        assert len(p["dimensions"]) >= 6
        assert "Graham" in p["documented_foundation"] or "Kiyosaki" in p["documented_foundation"] or "Sethi" in p["documented_foundation"] or "Indian" in p["documented_foundation"] or "Trinity" in p["documented_foundation"]

def test_multi_perspective_comparison_generation():
    question = "Should I prepay my home loan early or invest in index mutual funds?"
    res = philosophy_engine.compare_philosophies(
        question=question,
        philosophy_ids=["value_compounding", "cashflow_assets", "conscious_spending"],
        dimension="debt"
    )

    assert res["topic"] == question
    assert res["detected_dimension"] == "debt"
    assert len(res["perspectives"]) == 3

    # 1. Perspective A (Value Compounding)
    p_a = res["perspectives"][0]
    assert p_a["philosophy_id"] == "value_compounding"
    assert "The Intelligent Investor" in p_a["documented_foundation"]
    assert len(p_a["actionable_steps"]) > 0

    # 2. Perspective B (Cash Flow Assets)
    p_b = res["perspectives"][1]
    assert p_b["philosophy_id"] == "cashflow_assets"
    assert "Rich Dad Poor Dad" in p_b["documented_foundation"]

    # 3. Perspective C (Conscious Spending)
    p_c = res["perspectives"][2]
    assert p_c["philosophy_id"] == "conscious_spending"
    assert "I Will Teach You to Be Rich" in p_c["documented_foundation"]

    # 4. Key Differences & 5. Areas of Agreement & 6. Balanced Synthesis
    assert len(res["key_differences"]) > 0
    assert len(res["areas_of_agreement"]) >= 3
    assert "Balanced Strategic Synthesis" in res["balanced_synthesis"]
    assert "Educational Interpretation Notice" in res["educational_disclaimer"]

@pytest.mark.asyncio
async def test_philosophy_comparison_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        unique_email = "philosophy_user@finsight.ai"
        reg_payload = {
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Philosophy Comparator",
            "preferred_currency": "INR",
            "monthly_income": 90000.0
        }
        r_reg = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert r_reg.status_code == 200
        token = r_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. GET /philosophies
        r_list = await ac.get("/api/v1/advisor/philosophies", headers=headers)
        assert r_list.status_code == 200
        phil_list = r_list.json()
        assert len(phil_list) >= 4
        assert any(p["id"] == "value_compounding" for p in phil_list)

        # 2. POST /compare
        compare_payload = {
            "question": "How should I structure my monthly salary across investments and lifestyle spending?",
            "philosophies": ["value_compounding", "conscious_spending", "holistic_indian"],
            "dimension": "budgeting"
        }
        r_comp = await ac.post("/api/v1/advisor/compare", json=compare_payload, headers=headers)
        assert r_comp.status_code == 200
        comp_res = r_comp.json()
        assert comp_res["detected_dimension"] == "budgeting"
        assert len(comp_res["perspectives"]) == 3
        assert len(comp_res["areas_of_agreement"]) > 0
        assert "Educational Interpretation Notice" in comp_res["educational_disclaimer"]

        # 3. Legacy compatibility POST /compare-philosophies
        r_leg = await ac.post("/api/v1/advisor/compare-philosophies", json={"question": "Should I buy real estate on EMI?"}, headers=headers)
        assert r_leg.status_code == 200
        assert "opinions" in r_leg.json()
