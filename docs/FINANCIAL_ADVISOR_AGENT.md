# FinSight AI — LangGraph Financial Advisor Agent

## Architecture Overview
The FinSight AI Financial Advisor is built as a tool-using StateGraph agent powered by LangGraph. It is designed to strictly prevent LLM arithmetic hallucinations and ensure complete data privacy by isolating tool queries to authenticated users (`user_id`).

```
                    User Query
                        │
                        ▼
       ┌──────────────────────────────────┐
       │   Intent Router & Guardrails     │
       │   - PII Scrubbing                │
       │   - Prompt Injection Shield      │
       │   - Multi-Tool Intent Detection  │
       └────────────────┬─────────────────┘
                        │
                        ▼
       ┌──────────────────────────────────┐
       │     Authorized Tool Executor     │
       │   - Strict user_id Scoping       │
       │   - Deterministic Calculators    │
       │   - Latency & Audit Logging      │
       │   - Timeout & Failure Handling   │
       └────────────────┬─────────────────┘
                        │
                        ▼
       ┌──────────────────────────────────┐
       │      Response Synthesizer        │
       │   - Persona Philosophy Grounding │
       │   - Cited Data Extraction        │
       │   - Suggested Follow-Up Prompts  │
       └──────────────────────────────────┘
```

---

## Controlled Financial Tools

| Tool Name | Parameters | Data Source / Method | Security Constraint |
| :--- | :--- | :--- | :--- |
| `get_transactions` | `category_name`, `limit`, `start_date`, `end_date` | PostgreSQL `transactions` table | Scoped strictly to `user_id` |
| `get_income` | `start_date`, `end_date` | `FinancialAnalyticsEngine.calculate_summary` | Credits only, `user_id` scoped |
| `get_expenses` | `start_date`, `end_date` | `FinancialAnalyticsEngine.calculate_summary` | Debits only, `user_id` scoped |
| `get_category_spending` | `start_date`, `end_date` | `FinancialAnalyticsEngine.calculate_category_spending` | Aggregated category allocations |
| `get_budget_status` | None | `FinancialAnalyticsEngine.calculate_budget_utilization` | Scoped to active user budgets |
| `get_goals` | None | PostgreSQL `financial_goals` table | Scoped to user's active goals |
| `calculate_savings_rate` | `start_date`, `end_date` | Decimal-safe savings rate formula | Exact deterministic calculation |
| `calculate_financial_health` | None | `FinancialHealthEngine.compute_health_score` | 7-factor explainable score |
| `detect_anomalies` | None | Statistical 2.5x variance threshold | Recent 60-day user debits |
| `forecast_expenses` | `days_ahead` | 60-day moving average daily burn | Time-series confidence bounds |
| `get_recurring_expenses` | None | PostgreSQL `subscriptions` table | Active user subscriptions |
| `search_financial_knowledge` | `query`, `top_k` | In-memory RAG Vector Index | Grounded financial literature |
| `calculate_sip` | `monthly_investment`, `annual_rate_pct`, `years` | Monthly compound interest formula | Deterministic mathematical tool |
| `calculate_emi` | `principal`, `annual_interest_rate`, `tenure_years` | Standard reducing balance EMI formula | Deterministic mathematical tool |

---

## Guardrails & Data Handling Principles

1. **Zero Database Querying by LLM**: The LLM is never given raw SQL access or database connection handles. All data access is mediated through explicit, strongly-typed tool functions.
2. **Deterministic Data Grounding**: Financial figures cited in responses are directly extracted from the returned tool payloads (`cited_data`).
3. **Data Unavailability Identification**: If no records match a timeframe or category, the tool returns an explicit status (`"No transactions found for that timeframe"`), preventing the model from hallucinating numbers.
4. **Tool Call Audit Logging**: Every tool execution is instrumented with execution latency and logged for debugging and audit compliance.
