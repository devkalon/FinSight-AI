# FinSight AI — Financial Analytics Engine

## Overview
FinSight AI features a deterministic, decimal-safe Financial Analytics Engine designed to compute ledger statistics directly from PostgreSQL transactions. The engine strictly avoids LLM mathematical hallucinations and floating-point rounding errors by executing decimal arithmetic via Python's `Decimal` module and optimized SQLAlchemy database queries.

---

## Core Analytics Capabilities

### 1. Deterministic Financial Summary KPIs
- **Total Income**: Precise sum of credit transactions within the filtered date window.
- **Total Expenses**: Precise sum of debit transactions within the filtered date window.
- **Net Savings**: `Total Income - Total Expenses`.
- **Savings Rate**: `(Net Savings / Total Income) * 100` (computed as `0.0%` if income <= 0).
- **Average Daily Spend**: `Total Expenses / Days in Window`.

### 2. Month-over-Month (MoM) Shift Analysis
- Compares current window KPIs against an identical prior time period.
- Computes both **percentage change** and **absolute currency shift** for Income, Expenses, and Net Savings.

### 3. Essential vs Discretionary (50/30/20 Framework)
- **Needs (Essential)**: Rent, Utilities & Bills, Groceries/Food, EMI, Healthcare, Insurance.
- **Wants (Discretionary)**: Shopping, Dining, Entertainment, Travel, Media Subscriptions.
- **Savings & Investments**: Mutual Funds, SIPs, Equity, Fixed Deposits.

### 4. Category & Merchant Intelligence
- **Category Allocation**: Ranked spending breakdown with percentage of total expense, count, and category color tokens.
- **Top Spending Merchants**: Largest merchants ranked by total spend and transaction count.
- **Budget Utilization**: Actual period spending compared against monthly budget limits per category, flagging over-budget categories (`is_over_budget: True`).
- **Recurring Expenses**: Automated monthly subscription and bill commitments.

---

## API Endpoints

- `GET /api/v1/analytics/summary`: Returns summary financial KPIs (`total_income`, `total_expenses`, `net_savings`, `savings_rate_pct`, `average_daily_spending`).
- `GET /api/v1/analytics/dashboard`: Assembles complete dashboard payload (KPIs, MoM, spending split, category breakdown, cash flow trends, merchants, budget utilization).
- `GET /api/v1/analytics/month-over-month`: Returns period-over-period percentage and absolute changes.
- `GET /api/v1/analytics/spending-split`: Returns Needs / Wants / Savings split.
- `GET /api/v1/analytics/top-merchants`: Returns top N merchants by spending volume.
- `GET /api/v1/analytics/budget-utilization`: Returns category budget adherence status.
- `GET /api/v1/analytics/trends`: Returns historical monthly cash flow timeseries.

All endpoints support `start_date` and `end_date` date-range filtering.
