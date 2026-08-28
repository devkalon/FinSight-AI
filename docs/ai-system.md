# FinSight AI — AI Advisor & Multi-Agent Architecture

## Design Principles
1. **Zero Math Hallucinations**: LLMs are prohibited from conducting arithmetic or database lookups directly. All numbers originate from deterministic Python tool calls.
2. **Strict Grounding**: System prompts enforce explicit acknowledgment when requested transaction ranges or merchant records are unavailable.
3. **Multi-Guru Comparison**: Advice perspectives are structured across Warren Buffett, Robert Kiyosaki, Ramit Sethi, and Indian Wealth Advisor.

```mermaid
sequenceDiagram
    participant User
    participant Agent as LangGraph Agent
    participant Guard as PII & Injection Guard
    participant Tools as Python FinTools
    participant RAG as RAG Retrieval Engine
    participant LLM as Model / Synthesis Engine

    User->>Agent: Send Prompt ("How can I reach my ₹10L goal in 3 years?")
    Agent->>Guard: Validate Prompt for Injection & PII
    Guard-->>Agent: Sanitized Prompt Clean
    Agent->>Tools: Call get_goals() & calculate_sip()
    Tools-->>Agent: Exact Target ₹10,00,00, SIP ₹23,214/mo @ 12%
    Agent->>RAG: Search Knowledge Base for SIP Pacing Strategies
    RAG-->>Agent: Relevant Literature Chunks & Citations
    Agent->>LLM: Synthesize Grounded Response with Verified Numbers
    LLM-->>Agent: Formatted Markdown Advice with Disclaimers
    Agent-->>User: Structured Financial Advice
```

---

## Controlled AI Tools Registry

- `get_transactions(db, user_id, limit, category, start_date, end_date)`: Authorized fetch of user transactions.
- `get_category_spending(db, user_id, month, year)`: Aggregated category spending summary.
- `get_budget_status(db, user_id)`: Category limit utilization and threshold warnings.
- `get_goals(db, user_id)`: Milestone target tracking and required monthly contributions.
- `calculate_sip(monthly_investment, annual_rate_pct, years)`: Deterministic SIP compound interest calculator.
- `calculate_emi(principal, annual_interest_rate, tenure_years)`: Loan EMI amortization calculator.
- `calculate_emergency_fund_target(monthly_expenses, target_months)`: Emergency reserve calculator.
- `search_financial_knowledge(query, top_k)`: RAG vector semantic search.

---

## Multi-Guru Personas Framework

- **Warren Buffett**: Focuses on intrinsic value, low-cost index funds, moat, long-term compounding, and avoiding debt.
- **Robert Kiyosaki**: Focuses on cash flow, assets vs. liabilities, real estate leverage, and passive income creation.
- **Ramit Sethi**: Focuses on conscious spending (spend ruthlessly on what you love, cut costs on what you don't), automating finances, and big wins.
- **Indian Wealth Advisor**: Focuses on PPF, ELSS tax savings (80C), NPS, digital gold, health insurance, and local Indian financial instruments.
