# FinSight AI — Financial Anomaly Detection Engine Architecture

## Overview
The Financial Anomaly Detection Engine provides multi-dimensional, statistical, and pattern-based anomaly detection across user transaction ledgers. It guards against false positives by requiring calibrated historical baselines.

```
                    User Transactions Stream / Ingestion
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │    Historical Baseline Calibrator   │
                  │  - Minimum N >= 3 transactions      │
                  │  - Rolling median & standard dev    │
                  └──────────────────┬──────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ Category Surges  │        │ Amount Outliers  │        │ Merchant Surges  │
│ (e.g. Food +155%)│        │ (Z > 2.5σ / IQR) │        │ (Spikes > 2x avg)│
└──────────────────┘        └──────────────────┘        └──────────────────┘
         │                           │                           │
         ├───────────────────────────┼───────────────────────────┤
         ▼                           ▼                           ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ Frequency Bursts │        │ Recurring Hikes  │        │  Monthly Surges  │
│ (Daily clustering│        │ (Step-up bill +%)│        │ (Burn-rate spike)│
└──────────────────┘        └──────────────────┘        └──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │     Structured Anomaly Output       │
                  │  - Severity: Critical/High/Medium   │
                  │  - Observed vs Expected metrics     │
                  │  - Deviation % and explanation      │
                  │  - Affected transaction links       │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │    Anomaly Dashboard in Next.js     │
                  │  - KPI cards & Severity filters     │
                  │  - Real-time "Run Scan" trigger     │
                  └─────────────────────────────────────┘
```

---

## 6 Statistical Anomaly Dimensions

1. **Category Spending Surges (`category_spending`)**:
   - Compares current cycle spending in each category against historical monthly average.
   - Example: Food spending observed at ₹15,800 vs expected typical ₹6,200 (+154.8%).
2. **Transaction Amount Outliers (`transaction_amount`)**:
   - Detects single high-value purchases using robust Z-score ($Z \ge 2.5$) and median multipliers.
   - Example: Single debit of ₹45,000 at Apple Store when median transaction is ₹2,800.
3. **Merchant Spending Surges (`merchant_spending`)**:
   - Detects sudden surges at specific merchants ($> 2.0\times$ baseline).
   - Example: Amazon spending surges to ₹18,500 compared to typical ₹1,500.
4. **Frequency Spikes / Burst Spending (`frequency_spike`)**:
   - Detects abnormal clustering of transactions on a single day ($> 2.5\times$ daily average frequency).
5. **Recurring Subscription & Bill Changes (`recurring_change`)**:
   - Tracks fixed subscriptions (Netflix, Spotify, Internet, Gym) and flags step price hikes ($> +20\%$).
6. **Monthly Spending Burn-Rate Surges (`monthly_spending`)**:
   - Compares total monthly expenditure against multi-month rolling mean ($> +40\%$).

---

## False-Positive Prevention Guardrail
- Requires at least 3 transactions in the user ledger before running statistical outlier detection.
- Requires at least 3 historical transactions for a given category or merchant before calculating percentage deviation surges.
