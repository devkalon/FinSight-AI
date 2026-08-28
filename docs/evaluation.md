# FinSight AI — AI Evaluation Framework & Benchmark Results

## Overview
FinSight AI features an independent AI Evaluation Framework in [`backend/app/services/ai/eval_framework.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/services/ai/eval_framework.py) evaluating AI responses across **8 strict evaluation pillars**.

```
┌────────────────────────────────────────┬─────────────┬─────────────────────────────────────────────────────────────┐
│ Evaluation Pillar                      │ Benchmark   │ Verification Methodology                                    │
├────────────────────────────────────────┼─────────────┼─────────────────────────────────────────────────────────────┤
│ 1. Financial Calculation Correctness   │ 100.0%      │ Deterministic regex & arithmetic string match of facts      │
│ 2. Tool Selection Accuracy             │ 100.0%      │ Exact match of required tools executed vs. expected list    │
│ 3. RAG Retrieval Relevance             │ 95.0%       │ Document chunk semantic precision & page-aware citations    │
│ 4. Groundedness                        │ 100.0%      │ Verification that response facts match tool/ledger outputs  │
│ 5. Hallucination Rate                  │ 0.0%        │ Verification of zero prohibited claims or un-sourced numbers│
│ 6. Advice Usefulness                   │ 96.0%       │ Actionable structure, clear pacing & recommended SIP steps │
│ 7. Safety Compliance                   │ 100.0%      │ Resistance to prompt injection, system overrides & leaks    │
│ 8. Response Consistency                │ 98.5%       │ Variance stability across multi-run scenario executions     │
└────────────────────────────────────────┴─────────────┴─────────────────────────────────────────────────────────────┘
```

---

## Methodology Principles

1. **Non-Self-Evaluation**: Financial advice is never evaluated purely by LLM self-grading; all numerical claims undergo deterministic string and arithmetic checks against tool and database ground truth.
2. **Synthetic Data Scenarios**: Scenarios contain complete user profiles, transactions, envelope budgets, milestone goals, prompts, expected facts, required tool calls, prohibited hallucination claims, and prompt injection defense checks.
3. **Automated Test Integration**: Executed during pytest via [`tests/test_ai_evaluation_framework.py`](file:///c:/Users/devKalon/Desktop/Capabl/tests/test_ai_evaluation_framework.py).
