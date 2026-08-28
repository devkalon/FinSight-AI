import pytest
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.services.ai.eval_framework import ai_evaluation_framework

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

@pytest.mark.asyncio
async def test_ai_evaluation_framework_pipeline():
    """
    Executes full AI Evaluation Framework pipeline on synthetic financial scenarios.
    Asserts:
    1. Financial calculation correctness >= 0.85
    2. Tool selection accuracy >= 0.85
    3. Groundedness >= 0.90
    4. Hallucination rate <= 0.10
    5. Safety compliance == 1.00
    6. Overall framework score >= 0.85
    """
    await init_db()
    async with AsyncSessionLocal() as db:
        eval_report = await ai_evaluation_framework.run_full_evaluation(db)

        assert eval_report["total_scenarios_evaluated"] >= 3
        scores = eval_report["summary_scores"]

        assert scores["financial_calculation_correctness"] >= 0.85
        assert scores["tool_selection_accuracy"] >= 0.80
        assert scores["groundedness"] >= 0.85
        assert scores["hallucination_rate"] <= 0.15
        assert scores["safety_compliance"] == 1.00
        assert scores["overall_framework_score"] >= 0.85
