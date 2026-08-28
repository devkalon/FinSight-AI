# FinSight AI — API Specification

**Base URL:** `http://localhost:8000/api/v1`  
**Authentication:** Bearer JWT in `Authorization` header

---

## 1. Authentication Endpoints (`/auth`)

### `POST /auth/register`
* **Request:**
  ```json
  {
    "email": "user@example.com",
    "password": "Password123!",
    "full_name": "Alex Mercer",
    "preferred_currency": "INR",
    "preferred_guru": "balanced",
    "monthly_income": 85000.0
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "email": "user@example.com",
    "full_name": "Alex Mercer"
  }
  ```

### `POST /auth/login`
* **Request:** `{"email": "user@example.com", "password": "Password123!"}`
* **Response (200 OK):** Returns JWT access token and user metadata.

### `GET /auth/me`
* **Response (200 OK):** User profile, monthly income, preferred currency, default guru persona.

---

## 2. Transactions & Ingestion Endpoints (`/transactions`)

### `GET /transactions/`
* **Query Params:** `skip=0`, `limit=50`, `category_id`, `transaction_type`, `start_date`, `end_date`
* **Response (200 OK):** Array of transactions with nested category metadata.

### `POST /transactions/`
* **Request:**
  ```json
  {
    "amount": 1450.0,
    "transaction_type": "debit",
    "transaction_date": "2026-08-28",
    "description": "Starbucks Coffee & Snacks",
    "payment_method": "UPI"
  }
  ```
* **Response (200 OK):** Auto-categorized created transaction object.

### `POST /transactions/batch`
* **Request:** `{"transactions": [...]}`
* **Response (200 OK):** Ingests and auto-categorizes multiple transactions in a single batch.

---

## 3. Document Processing & OCR Endpoints (`/documents`)

### `POST /documents/upload/receipt`
* **Payload:** `multipart/form-data` with `file` (Image/PDF)
* **Response (200 OK):**
  ```json
  {
    "document_id": "uuid",
    "filename": "receipt.jpg",
    "extracted_transaction": {
      "merchant_name": "Swiggy",
      "amount": 504.0,
      "transaction_date": "2026-08-28",
      "category_suggestion": "Food & Dining",
      "payment_method": "UPI",
      "confidence_score": 0.92,
      "redaction_stats": {"PAN": 0, "CREDIT_CARD": 0}
    }
  }
  ```

### `POST /documents/upload/bank-statement`
* **Payload:** `multipart/form-data` with `file` (.pdf or .csv)
* **Response (200 OK):** Extracted multi-line transactions array with statement account summary.

---

## 4. Analytics & ML Endpoints (`/analytics`)

* `GET /analytics/health-score`: Composite 0-100 score + 4-dimension breakdown.
* `GET /analytics/cashflow`: 6-month historical cashflow trends.
* `GET /analytics/categories`: Category spend breakdown & 50/30/20 grouping.
* `GET /analytics/anomalies`: Outlier spending spikes & duplicate transaction alerts.
* `GET /analytics/subscriptions`: Identified recurring monthly/annual subscriptions.
* `GET /analytics/forecast`: 30/60/90-day predictive expense forecast.
* `POST /analytics/simulation`: What-If financial simulation engine.

---

## 5. AI Advisor Endpoints (`/advisor`)

### `POST /advisor/chat`
* **Request:**
  ```json
  {
    "message": "Calculate my SIP return if I invest 10000 per month for 10 years",
    "persona": "buffett"
  }
  ```
* **Response (200 OK):** Message content with executed deterministic tool results and RAG citations.

### `POST /advisor/compare-philosophies`
* **Request:** `{"question": "Should I pre-close my home loan or invest in equity index funds?"}`
* **Response (200 OK):** Side-by-side comparative perspectives from Buffett, Kiyosaki, Sethi, and Indian Wealth Advisor.
