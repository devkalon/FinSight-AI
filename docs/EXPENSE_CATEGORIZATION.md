# FinSight AI — Hybrid Expense Categorization Engine

## Overview
FinSight AI implements a 4-layer hybrid categorization engine designed for financial transactions. Every prediction tracks structured metadata (`category`, `subcategory`, `confidence`, `classification_method`, `rationale`, and `is_low_confidence`), flags low-confidence candidates to prevent silent data corruption, and continuously learns user-specific mapping preferences.

---

## 4-Layer Hybrid Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Transaction Description / Narration                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              Layer 4: User Correction Learning (Priority 1)                 │
│   - Custom user rules stored in `category_learning_rules` table             │
│   - When matched, returns `confidence: 1.0`, method: `user_learned_rule`   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (If no user rule matched)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              Layer 1: Deterministic Merchant Rules (Priority 2)             │
│   - High-precision dictionary & regex matching with boundary protection     │
│   - Extracts both primary Category and Subcategory                          │
│   - Returns `confidence: 0.98`, method: `deterministic_rule`                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (If no keyword rule matched)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              Layer 2: Calibrated ML Classifier (Priority 3)                 │
│   - TF-IDF Vectorizer (n-grams 1-2) + Calibrated Logistic Regression        │
│   - Class probability distributions across 14 financial categories          │
│   - Returns `confidence >= 0.70`, method: `ml_classifier`                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (If ML confidence < 0.70)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              Layer 3: LLM Contextual Fallback & Safeguard (Priority 4)      │
│   - Contextual semantic evaluation with reasoning rationale                 │
│   - Low confidence (< 0.70) transactions tagged `is_low_confidence: True`   │
│   - Low confidence predictions are NEVER silently trusted as verified data  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Standard Category & Subcategory Taxonomy

1. **Food**: Food Delivery, Restaurants, Cafe & Bakery, Groceries
2. **Transport**: Cabs & Rides, Fuel, Public Transit, Tolls & Parking
3. **Shopping**: Online Retail, Clothing & Fashion, Electronics, Home & Kitchen
4. **Bills**: Electricity, Mobile & Broadband, Water & Gas, DTH, Utilities
5. **Entertainment**: Movies & Events, Gaming, Amusement
6. **Education**: Courses & Books, Tuition & School Fees
7. **Healthcare**: Pharmacy & Medicine, Doctor & Hospital, Fitness & Gym
8. **Rent**: House Rent, Maintenance & Society Dues
9. **EMI**: Home Loan, Car Loan, Personal Loan, Credit Card EMI
10. **Insurance**: Health Insurance, Life Insurance, Vehicle Insurance
11. **Investment**: Mutual Funds & SIP, Stocks & Equity, Fixed Deposits, Gold
12. **Travel**: Flights & Airlines, Hotels & Stays, Trains & Buses
13. **Subscriptions**: Media Streaming, SaaS & Cloud, Memberships
14. **Other**: Cash Withdrawal, Transfers, Miscellaneous

---

## API Endpoints

- `POST /api/v1/analytics/categorize`:
  Categorizes any transaction description using the 4-layer engine and returns prediction details and confidence scores.
- `GET /api/v1/analytics/categorization-metrics`:
  Runs evaluation against the benchmark dataset and returns Accuracy, Precision, Recall, F1-Scores, and Expected Calibration Error (ECE).
- `POST /api/v1/analytics/categories/learn-rule`:
  Learns and persists a custom merchant/pattern &rarr; category mapping for the authenticated user.
