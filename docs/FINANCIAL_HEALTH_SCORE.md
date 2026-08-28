# FinSight AI — Explainable Financial Health Score Engine

## Overview
The Financial Health Score Engine delivers a transparent, deterministic 0–100 scoring model computed from verified financial data. The engine eliminates arbitrary LLM number generation by evaluating 7 mathematical components with explicit weights, generating component-level status ratings, identifying positive and negative factors, tracking historical scores, and explaining score changes.

---

## 7 Core Scoring Dimensions

| Dimension | Weight | Benchmark / Criteria | Metric Measured |
| :--- | :--- | :--- | :--- |
| **Savings Rate** | 20% | $\ge 35\%$ (100 pts), $\ge 20\%$ (75–99 pts), $\ge 10\%$ (50–74 pts) | Net savings $\div$ monthly income |
| **Budget Adherence** | 15% | $\le 80\%$ (100 pts), $\le 100\%$ (80–99 pts), $\le 120\%$ (50–79 pts) | Actual debit $\div$ monthly budget limits |
| **Debt Burden (DTI)** | 15% | $0\%$ DTI (100 pts), $\le 15\%$ (90–99 pts), $\le 30\%$ (75–89 pts), $\le 45\%$ (50–74 pts) | Total EMI & loan payments $\div$ monthly income |
| **Emergency Fund** | 15% | $\ge 6.0$ months (100 pts), $\ge 4.0$ mo (85–99 pts), $\ge 2.5$ mo (70–84 pts) | Liquid reserves $\div$ monthly living expenses |
| **Spending Consistency** | 15% | Low CV $\le 0.25$ (100 pts), $0.25 < CV \le 0.50$ (75–99 pts) | Weekly spend variance ($CV = \sigma/\mu$) |
| **Recurring Burden** | 10% | $\le 10\%$ (100 pts), $\le 20\%$ (80–99 pts), $\le 35\%$ (50–79 pts) | Fixed bills & subscriptions $\div$ monthly income |
| **Goal Progress** | 10% | $\ge 75\%$ avg (100 pts), $\ge 50\%$ (80–99 pts), $\ge 25\%$ (55–74 pts) | Average progress % across active goals |

$$\text{Composite Score} = \sum_{i=1}^{7} (\text{Component Score}_i \times \text{Weight}_i)$$

---

## Response Structure

```json
{
  "score": 78,
  "rating": "Good",
  "components": {
    "savings_rate": {
      "name": "Savings Rate",
      "score": 82,
      "weight": 0.20,
      "weighted_score": 16.4,
      "status": "Good",
      "metric_value": "28.5%",
      "description": "Saving 28.5% of monthly income (Benchmark: 20-30%+)"
    },
    "budget_adherence": {
      "name": "Budget Adherence",
      "score": 75,
      "weight": 0.15,
      "weighted_score": 11.25,
      "status": "Good",
      "metric_value": "74.0% utilized",
      "description": "Spent ₹34,200 against monthly budget limit of ₹46,000"
    },
    "debt_burden": {
      "name": "Debt Burden",
      "score": 91,
      "weight": 0.15,
      "weighted_score": 13.65,
      "status": "Excellent",
      "metric_value": "12.0% DTI",
      "description": "Debt & EMI obligations consume 12.0% of income"
    },
    "emergency_fund": {
      "name": "Emergency Fund",
      "score": 63,
      "weight": 0.15,
      "weighted_score": 9.45,
      "status": "Fair",
      "metric_value": "2.8 Months",
      "description": "Liquid cushion covers 2.8 months of expenses (Target: 6 mo)"
    },
    "spending_consistency": {
      "name": "Spending Consistency",
      "score": 79,
      "weight": 0.15,
      "weighted_score": 11.85,
      "status": "Good",
      "metric_value": "82% Stability",
      "description": "Measures weekly spend volatility and unplanned variance"
    },
    "recurring_burden": {
      "name": "Recurring Burden",
      "score": 85,
      "weight": 0.10,
      "weighted_score": 8.5,
      "status": "Excellent",
      "metric_value": "14.2% Fixed",
      "description": "Fixed commitments & subscriptions consume 14.2% of income"
    },
    "goal_progress": {
      "name": "Goal Progress",
      "score": 70,
      "weight": 0.10,
      "weighted_score": 7.0,
      "status": "Good",
      "metric_value": "60.0% Avg",
      "description": "2 active financial goals with 60.0% overall progress"
    }
  },
  "positive_factors": [
    "Manageable debt obligations (12.0% DTI).",
    "Healthy savings rate of 28.5% (target: 20%+).",
    "Stable week-over-week spending discipline with low variance."
  ],
  "negative_factors": [
    "Emergency reserve covers only 2.8 months (recommended: 6 months)."
  ],
  "recommendations": [
    "Allocate ₹5,000/month into liquid funds until a 6-month buffer is established."
  ],
  "score_delta": 4,
  "delta_explanation": "Score increased by +4 points driven by improvements in savings and budget discipline."
}
```

---

## API Endpoints

- `GET /api/v1/analytics/health-score`: Computes 7-factor explainable score, stores snapshot in database, and returns delta explanation.
- `GET /api/v1/analytics/health-score/history?limit=20`: Returns chronological history of financial health scores and component progressions.
