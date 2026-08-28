# FinSight AI — Recurring Payment & Subscription Detection Architecture

## Overview
The Recurring Payment and Subscription Detection engine automatically analyzes user transaction histories to detect recurring payments, calculates monthly and annualized recurring burn, categorizes recurring commitments, and provides an anti-false-positive guardrail to reject variable repeated purchases.

```
                    User Transaction Stream
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │   Recurring Payment & Subscription Engine    │
        │ - Known Subscription Signatures              │
        │ - Time-Series Cadence & Interval Analysis    │
        │ - Coefficient of Variation (CV) Filter       │
        └──────────────────────┬───────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Monthly / OTT  │   │  Annual Plans   │   │  Utility Bills  │
│  Subscriptions  │   │ & License Fees  │   │ & Memberships   │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │       Annualized Burn & Lifecycle Engine     │
        │ - Annualized cost = monthly * 12, etc.       │
        │ - Next billing renewal countdown             │
        │ - State: Detected -> Confirmed / Dismissed   │
        └──────────────────────┬───────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │     Subscriptions Next.js Dashboard UI       │
        │ - Total Monthly & Annualized Burn Banners    │
        │ - Pending Review Action Queue                │
        │ - Edit, Confirm, Dismiss, Create Modals     │
        └──────────────────────────────────────────────┘
```

---

## 1. Detection Capabilities
1. **Monthly Subscriptions**: (e.g., Netflix, Spotify, iCloud, YouTube Premium, ChatGPT Plus)
2. **Annual Subscriptions**: (e.g., Amazon Prime Annual, Hotstar, Domain renewals)
3. **Recurring Utility Bills**: (e.g., Broadband/Fiber, Postpaid Mobile, Electricity, Rent)
4. **Recurring Memberships**: (e.g., Cult.fit, Gym, Co-working space)

---

## 2. Anti-False-Positive Guardrail
- **Amount Consistency**: Rejects repeating merchant purchases if the amount fluctuates beyond a $12\%$ coefficient of variation ($CV = \sigma / \mu > 0.12$).
- **Periodicity Cadence**: Verifies that time intervals between transactions adhere to standard cadence ($\pm 4$ days for monthly, $\pm 10$ days for annual).
- **Exclusion List**: Explicitly flags variable lifestyle purchases (e.g., Swiggy, Zomato, Blinkit, grocery stores, fuel pumps) as normal consumption, preventing false subscription alerts.

---

## 3. Mathematical Calculations
- **Annualized Cost**:
  - Monthly: $\text{Amount} \times 12$
  - Yearly/Annual: $\text{Amount} \times 1$
  - Quarterly: $\text{Amount} \times 4$
  - Weekly: $\text{Amount} \times 52$
- **Total Monthly Recurring Burn**:
  $$\text{Total Monthly Burn} = \sum_{s \in \text{Active}} \frac{\text{Annualized Cost}_s}{12}$$
- **Total Annual Recurring Burn**:
  $$\text{Total Annual Burn} = \sum_{s \in \text{Active}} \text{Annualized Cost}_s$$
