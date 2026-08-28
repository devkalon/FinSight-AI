# FinSight AI — Financial Anomaly Detection Engine Implementation Report

## Summary
The Financial Anomaly Detection Engine has been implemented. It monitors user transactions across 6 statistical and pattern-based dimensions: category spending surges (e.g., Food +155%), merchant spending surges, individual transaction amount outliers (Z-score > 2.5), frequency burst spikes, recurring subscription hikes, and monthly burn-rate surges. It provides severity levels, observed vs. expected values, percentage deviations, human-readable explanations, and lists of affected transactions. An Anomaly Radar Dashboard with real-time scanning triggers has been integrated into Next.js.

---

## Implementation Details

### 1. Statistical Anomaly Detection Engine
- [`backend/app/services/ml/anomaly_detector.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/services/ml/anomaly_detector.py):
  - **Category Spending Surges**: Grouped by category and monthly windows; flags surges exceeding $+50\%$ above typical baseline.
  - **Transaction Amount Outliers**: Robust Z-Score ($Z \ge 2.5$) and Median/IQR calculations.
  - **Merchant Spending Surges**: Multi-month merchant grouping; flags spikes $> 2.0\times$ typical average.
  - **Frequency Spikes**: Daily transaction clustering detection ($> 2.5\times$ daily mean).
  - **Recurring Subscription Price Hikes**: Tracks recurring charges and flags price increases ($> +20\%$).
  - **Monthly Burn-Rate Surges**: Multi-month total expenditure baseline comparisons.
  - **False Positive Prevention**: Requires at least 3 transactions in user history and 3 transactions for a given entity before calculating percentage deviations.

### 2. Schemas & Endpoints
- [`backend/app/schemas/analytics.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/schemas/analytics.py):
  - Added `AffectedTransactionDetail`, `DetailedAnomalyOut`, and `AnomalySummaryResponse`.
- [`backend/app/api/v1/endpoints/analytics.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/api/v1/endpoints/analytics.py):
  - `GET /api/v1/analytics/anomalies`: Returns full statistical anomaly evaluation for the user's ledger.
  - `POST /api/v1/analytics/anomalies/scan`: Triggers a real-time scan on transactions.

### 3. Frontend Anomaly Dashboard
- [`frontend/src/app/analytics/page.tsx`](file:///c:/Users/devKalon/Desktop/Capabl/frontend/src/app/analytics/page.tsx):
  - Anomaly KPI summary bar (Total Anomalies, Critical/High counts, Net Excess Deviation).
  - "Run Anomaly Scan" live trigger button.
  - Severity filter bar (`All`, `Critical`, `High`, `Medium`).
  - Anomaly cards displaying observed vs expected values, deviation chips, explanation text, and affected transactions.
  - Informative positive shield card when no anomalies are detected.
- [`frontend/src/lib/api.ts`](file:///c:/Users/devKalon/Desktop/Capabl/frontend/src/lib/api.ts):
  - Added `getAnomalies()` and `scanAnomalies()` API client methods.

---

## Verification & Test Results

### 1. Backend Pytest Suite
- Ran: `python -m pytest tests backend/tests -v`
- **Result**: **74 passed, 0 failed (100% pass rate)**
  - `tests/test_financial_anomaly_detector.py` (7 tests passed)
  - Full regression test suite (67 tests passed)

### 2. Frontend Checks & Production Build
- Ran: `npx tsc --noEmit` & `npm run build` in `frontend/`
- **Result**: **Clean compilation with 0 TypeScript/lint errors** (10 static routes generated).
