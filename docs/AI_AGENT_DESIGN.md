# FinSight AI — Multi-Agent System & AI Architecture

---

## 1. Multi-Agent Design Architecture

FinSight AI employs a multi-tiered agent architecture to guarantee accurate arithmetic, source grounding, and versatile financial philosophy perspectives.

```
                  ┌────────────────────────────────────────┐
                  │          USER QUERY / PROMPT           │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │       INTENT ROUTING & CLASSIFIER      │
                  └──────────────────┬─────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        ▼                            ▼                            ▼
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│     TOOL EXECUTOR       │ │      RAG RETRIEVER      │ │   MULTI-GURU SYNTHESIS  │
│ (Deterministic Python)  │ │ (Vector / TF-IDF Hybrid)│ │  (Buffett, Kiyosaki,    │
│ • SIP Compounding       │ │ • Psychology of Money   │ │   Ramit Sethi,          │
│ • Loan EMI              │ │ • Rich Dad Poor Dad     │ │   Indian Wealth Expert) │
│ • Emergency Fund        │ │ • Indian Tax Rules      │ └────────────┬────────────┘
│ • Tax Slab Optimizer    │ └────────────┬────────────┘              │
└───────────┬─────────────┘              │                           │
            └────────────────────────────┼───────────────────────────┘
                                         ▼
                  ┌────────────────────────────────────────┐
                  │         VERIFICATION & RESPONSE        │
                  │ • Grounded Arithmetic                  │
                  │ • Structured Disclaimers               │
                  │ • Actionable Next Steps                │
                  └────────────────────────────────────────┘
```

---

## 2. Guardrails Against Hallucinations

1. **Deterministic Financial Math Execution:** The AI model is strictly prohibited from guessing compound interest or loan balances; all numerical calculations are delegated to pure Python algorithms (`financial_tools`).
2. **Context Grounding (RAG):** Authoritative advice quotes are retrieved directly from verified knowledge items with explicit source citations.
3. **Regulatory Safety Guardrails:** Clear automated disclaimers clarify that FinSight AI provides educational guidance based on financial literature, advising users to consult licensed SEBI / CFP professionals for individual transactions.
