# FinSight AI — Predictive Expense Forecasting Engine Architecture

## Overview
The Predictive Expense Forecasting Engine estimates future spending horizons (30, 60, 90 days) using time-series decomposition, weekend seasonality weighting, category-level allocations, and recurring commitment anchors.

```
                    Historical Transaction Stream
                                  │
                                  ▼
             ┌──────────────────────────────────────────┐
             │       Time-Series Decomposer & ML        │
             │ - Trend Factor (Velocity Momentum)       │
             │ - Day-of-Week Seasonality (Weekend 1.3x) │
             │ - Recurring Expense Baseline Anchor      │
             └────────────────────┬─────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Total Monthly    │     │ Category-Level   │     │ Recurring Fixed  │
│ Forecast (30-90d)│     │ Allocations (85%)│     │ Liabilities (Yr) │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                                  ▼
             ┌──────────────────────────────────────────┐
             │       Holdout Evaluation Pipeline        │
             │ - Advanced Model (Seasonal Trend)        │
             │ - Baseline Model (Naive Moving Average)  │
             │ - MAE, MAPE, RMSE Error Metrics          │
             └────────────────────┬─────────────────────┘
                                  │
                                  ▼
             ┌──────────────────────────────────────────┐
             │    Next.js Dashboard & Explanations      │
             │ - Confidence Band Area Chart             │
             │ - Probabilistic Disclaimer Notice        │
             │ - Plain English AI Synthesis             │
             └──────────────────────────────────────────┘
```

---

## Forecasting Capabilities

1. **Multi-Horizon Total Expense Projections**:
   - Computes 30-day, 60-day, and 90-day forecast horizons.
   - Provides calibrated 85% prediction intervals (`lower_bound`, `upper_bound`) and statistical confidence scores.
   - Calculates dynamic financial runway months against monthly income.

2. **Category-Level Projections**:
   - Forecasts next month spending across categories (Food & Dining, Housing & Rent, Transportation, Shopping, Utilities, etc.).
   - Computes percentage budget share and category trend velocity.

3. **Recurring Commitment Anchoring**:
   - Isolates recurring subscriptions (broadband, telecom, streaming, gym, rent) to separate predictable fixed commitments from discretionary variable burn.

4. **Holdout Evaluation Pipeline**:
   - Evaluates the Advanced Seasonal Trend model against a Naive Simple Moving Average baseline on historical holdout slices.
   - Metrics computed:
     - $\text{MAE} = \frac{1}{n} \sum |y - \hat{y}|$
     - $\text{MAPE} = \frac{1}{n} \sum \left|\frac{y - \hat{y}}{y}\right| \times 100\%$
     - $\text{RMSE} = \sqrt{\frac{1}{n} \sum (y - \hat{y})^2}$
     - Accuracy improvement percentage.

5. **Mandatory Non-Guaranteed Disclaimer**:
   - *"Statistical Projection Notice: Future expense forecasts are probabilistic mathematical estimates derived from historical spending patterns and recurring commitments. They do not constitute guaranteed outcomes."*
