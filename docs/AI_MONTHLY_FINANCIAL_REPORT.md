# FinSight AI — AI-Assisted Monthly Financial Report Architecture

## Overview
The AI-Assisted Monthly Financial Report delivers a two-stage financial intelligence generation pipeline:
1. **Deterministic Backend Metrics Engine**: Calculates all numerical metrics across income, expenses, category spending, savings rate, budget utilization, goal progress, statistical anomalies, recurring subscriptions, and predictive forecasts directly from verified database records.
2. **Grounded AI Narrative Layer**: Generates an 11-section executive narrative strictly based on the calculated metrics without inventing statistics.
3. **Multi-Channel Delivery**: Interactive Next.js executive statement view and downloadable PDF generation via ReportLab.

```
                   User Verified Database Ledger
      (Transactions, Budgets, Goals, Anomalies, Subscriptions)
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │   Deterministic Monthly Calculation Engine   │
        │ - 11 Core Section Statistical Metrics        │
        │ - Zero LLM numerical calculation             │
        └──────────────────────┬───────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │       Grounded AI Narrative Generator        │
        │ - Synthesizes exact calculated numbers       │
        │ - Structured 11-section narrative            │
        └──────────────────────┬───────────────────────┘
                               │
         ┌─────────────────────┴─────────────────────┐
         ▼                                           ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│     Next.js Executive View    │   │      ReportLab PDF Engine     │
│ - Month selection picker      │   │ - Vector tables & formatting  │
│ - Verified KPI summary cards  │   │ - Multi-page statement export │
│ - Interactive section tables  │   │ - Direct download endpoint    │
└───────────────────────────────┘   └───────────────────────────────┘
```

---

## 1. The 11 Required Report Sections
1. **Executive summary**: High-level synopsis of total income, outlays, net savings, savings rate, and financial health score.
2. **Income**: Total recognized earnings, salary credits, and cash inflow stability.
3. **Spending**: Total outlays, average daily expenditure, essential vs discretionary allocation, and category breakdowns.
4. **Savings**: Net monthly retained capital, savings rate comparison against the 50/30/20 benchmark.
5. **Budget performance**: Total envelope limits, monthly utilization percentage, and over-budget category alerts.
6. **Goal progress**: Active milestone progress, total accumulated corpus, and required monthly SIP pacing.
7. **Anomalies**: Statistical spending spikes, frequency bursts, and merchant surges detected during the period.
8. **Recurring expenses**: Total monthly & annual recurring burn across subscriptions, utility bills, and memberships.
9. **Forecast**: Predictive 30-day expense estimation with confidence metrics and non-guaranteed disclaimers.
10. **Key observations**: Verified structural findings and lifestyle spending patterns.
11. **Recommended actions**: Actionable, prioritized steps for the upcoming month.

---

## 2. API Endpoints
- **`GET /api/v1/reports/monthly?month=YYYY-MM`**: Returns `MonthlyReportResponse` JSON.
- **`GET /api/v1/reports/monthly/pdf?month=YYYY-MM`**: Downloads PDF statement.
