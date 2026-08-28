# FinSight AI — Advanced Budgeting & Financial Goal Tracking Architecture

## Overview
The Advanced Budgeting and Financial Goal Tracking system delivers deterministic envelope budget monitoring, spending threshold warnings, multi-month historical adherence tracking, dynamic required savings calculations for milestones, and contextual AI recommendations.

```
                  User Transactions & Income Baseline
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│     Category Budget Envelopes   │         │    Financial Goal Milestones    │
│  - Monthly limits & threshold % │         │  - Target amount & target date  │
│  - Spent vs remaining amounts   │         │  - Current balance & % progress │
│  - Active warning state machine │         │  - Months remaining & SIP rate  │
└────────────────┬────────────────┘         └────────────────┬────────────────┘
                 │                                           │
                 ▼                                           ▼
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│      Warning & Alert Engine     │         │   Deterministic Dynamic Engine  │
│ - Normal (< threshold)          │         │ - Req Saving = Remaining/Months │
│ - Warning (>= threshold, e.g.80)│         │ - Projected completion date     │
│ - Critical (> limit)            │         │ - On-track feasibility flag     │
└────────────────┬────────────────┘         └────────────────┬────────────────┘
                 │                                           │
                 └─────────────────────────┬─────────────────┘
                                           │
                                           ▼
                            ┌─────────────────────────────┐
                            │ AI Contextual Recommendation│
                            │   Surplus & Pacing Advice   │
                            └──────────────┬──────────────┘
                                           │
                                           ▼
                            ┌─────────────────────────────┐
                            │    Next.js Dashboard UI     │
                            │ - Real-time budget bars     │
                            │ - Goal milestone trackers   │
                            │ - SIP wealth simulator      │
                            └─────────────────────────────┘
```

---

## 1. Budgeting Capabilities
- **Category & Monthly Envelopes**: Configurable monthly spending limits with customized alert warning thresholds (default 80%).
- **Warning State Machine**:
  - `normal`: Spent $< 80\%$ of monthly limit.
  - `warning`: Spent $\ge 80\%$ of limit. Displays threshold warning alert.
  - `critical_overbudget`: Spent $> 100\%$ of limit. Displays over-budget alert.
- **Historical Performance**: Aggregates multi-month adherence metrics and category insights (`GET /api/v1/budgets/historical-performance`).

---

## 2. Financial Goal Tracking
- **Standard & Custom Milestones**:
  - `Emergency Fund`
  - `Laptop Purchase`
  - `Travel`
  - `Education`
  - `Home Down Payment`
  - `Custom Goals`
- **Dynamic Deterministic Metrics**:
  - $\text{remaining\_amount} = \max(\text{target} - \text{current}, 0)$
  - $\text{months\_remaining} = \max((\text{year}_2 - \text{year}_1) \times 12 + (\text{month}_2 - \text{month}_1), 1)$
  - $\text{required\_monthly\_saving} = \frac{\text{remaining\_amount}}{\text{months\_remaining}}$
  - $\text{projected\_completion\_date} = \text{today} + \lceil\frac{\text{remaining}}{\text{monthly\_contrib}}\rceil \text{ months}$
- **AI Recommendation Engine**: Compares required monthly savings against monthly income and discretionary surplus to deliver actionable guidance.
