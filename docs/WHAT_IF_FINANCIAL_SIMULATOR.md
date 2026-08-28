# FinSight AI — Deterministic What-If Financial Simulator Architecture

## Overview
The Deterministic What-If Financial Simulator provides mathematical scenario modeling without relying on LLM computation. Users experiment with income hikes, expense cutbacks, subscription cancellations, budget reallocations, and goal contribution boosts. The simulator deterministically calculates cash flow shifts, annual savings deltas, goal completion acceleration, and financial health score impacts.

```
                      User Experimentation Levers
      (Income %, Food/Shopping Reductions, Subs Pruning, Goal Boost)
                                   │
                                   ▼
          ┌─────────────────────────────────────────────────┐
          │      Deterministic Financial Simulator Engine   │
          │             (Decimal-Safe Calculations)         │
          └────────────────────────┬────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ Monthly Cashflow │      │ Annual Savings   │      │ Goal Timeline    │
│ & Net Surplus    │      │ Impact (12-Mo &  │      │ Acceleration &   │
│ Comparison       │      │ Multi-Year CAGR) │      │ Target Dates     │
└────────┬─────────┘      └────────┬─────────┘      └────────┬─────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                                   ▼
          ┌─────────────────────────────────────────────────┐
          │     Post-Simulation AI Explanation Layer        │
          │  (Synthesizes deterministic outputs in plain    │
          │   language + Buffett/Kiyosaki/Sethi critiques)  │
          └────────────────────────┬────────────────────────┘
                                   │
                                   ▼
          ┌─────────────────────────────────────────────────┐
          │           Interactive Next.js UI                │
          │ - Side-by-side Current vs Simulated Columns     │
          │ - Real-time responsive slider controls          │
          │ - Goal acceleration milestone pills             │
          └─────────────────────────────────────────────────┘
```

---

## 1. Deterministic Calculation Rules
- **Monthly Income Delta**:
  $$\text{sim\_income} = \text{curr\_income} \times (1 + \text{income\_pct}/100) + \text{income\_abs}$$
- **Monthly Expense Reductions**:
  $$\text{total\_reduction} = \text{food\_cut} + \text{shopping\_cut} + \text{discretionary\_cut} + \text{cancelled\_subs}$$
  $$\text{sim\_expenses} = \max(\text{curr\_expenses} - \text{total\_reduction}, 5000)$$
- **Monthly Cash Flow Surplus**:
  $$\text{sim\_net\_cash\_flow} = \text{sim\_income} - \text{sim\_expenses}$$
  $$\Delta_{\text{monthly}} = \text{sim\_net\_cash\_flow} - \text{curr\_net\_cash\_flow}$$
- **Annual Savings Impact**:
  $$\Delta_{\text{annual}} = \Delta_{\text{monthly}} \times 12$$
- **Goal Completion Acceleration**:
  $$\text{sim\_monthly\_saving} = \text{base\_monthly\_saving} + \text{extra\_goal\_contrib} + (\max(\Delta_{\text{monthly}}, 0) \times 0.4)$$
  $$\text{sim\_months\_to\_complete} = \lceil\frac{\text{remaining\_target}}{\text{sim\_monthly\_saving}}\rceil$$
  $$\text{months\_saved} = \max(\text{base\_months} - \text{sim\_months}, 0)$$
- **Financial Health Score Projection**:
  - Re-evaluates savings rate weight ($40\%$), emergency coverage buffer ($35\%$), and fixed burn safety ($25\%$).

---

## 2. API Specifications
- **`POST /api/v1/analytics/simulation`**:
  - Payload: `SimulationRequest`
  - Response: `SimulationResponse` containing `current_scenario`, `simulated_scenario`, `net_monthly_delta`, `annual_savings_delta`, `health_score_delta`, `goal_impacts`, `ai_explanation`, and `guru_critique`.
