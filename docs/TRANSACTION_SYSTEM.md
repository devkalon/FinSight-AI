# FinSight AI — Core Transaction Management System

## Overview
The **Core Transaction Management System** provides enterprise-grade ledger operations for FinSight AI. It supports complete manual CRUD, rich multi-attribute querying, database-level pagination, dynamic multi-column sorting, and comprehensive metadata tracking.

---

## Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                         │
│  - Multi-Filter Toolbar (Search, Type, Method, Source, Date)│
│  - Dynamic Sorting & Database-Level Pagination Bar          │
│  - Manual Entry, Edit, & Transaction Details Modals         │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST / JSON (Authenticated Bearer JWT)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Transaction Router                  │
│       `backend/app/api/v1/endpoints/transactions.py`        │
│  - Route precedence: `/categories`, `/batch` before `/{id}` │
│  - Query parameter validation & user scope injection        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Transaction Service Layer                   │
│         `backend/app/services/transaction_service.py`       │
│  - Business logic, category binding, timestamp validation   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                Transaction Repository Layer                 │
│       `backend/app/repositories/transaction_repo.py`        │
│  - Async SQLAlchemy querying with `Numeric(14,2)` precision │
│  - Database-level `COUNT(*)` & `OFFSET / LIMIT` pagination  │
│  - Case-insensitive search across merchant, desc, & notes   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                      │
│  - `transactions` table with indexes on (user_id, tx_date), │
│    merchant_name, category_id, & soft delete support        │
└─────────────────────────────────────────────────────────────┘
```

---

## Transaction Data Model Fields

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Primary key identifier |
| `user_id` | UUID (FK) | Enforces strict data ownership (IDOR-safe) |
| `amount` | Numeric(14, 2) | Exact currency representation (no floats) |
| `currency` | String(3) | ISO 4217 currency code (e.g. `INR`, `USD`, `EUR`) |
| `transaction_type` | String(20) | `debit`, `credit`, or `transfer` |
| `transaction_date` | Date | Effective transaction date |
| `description` | String(500) | Full transaction description |
| `merchant_name` | String(255) | Normalized merchant / payee name (indexed) |
| `category_id` | UUID (FK, opt) | Reference to categorized budget category |
| `subcategory` | String(100) | Granular classification (e.g., "Dining Out", "Fuel") |
| `payment_method` | String(50) | `UPI`, `Credit Card`, `Debit Card`, `Net Banking`, `Cash` |
| `source` | String(50) | `manual`, `ocr_receipt`, `bank_pdf`, `csv` |
| `confidence_score` | Float | AI/ML classification confidence (0.0 to 1.0) |
| `notes` | Text | User remarks and notes |
| `extra_metadata` | Text / JSON | Raw payload / metadata storage |
| `is_subscription` | Boolean | Recurring transaction indicator |
| `created_at` / `updated_at` | Timestamp | Audit trail |

---

## REST Endpoints

### 1. Paginated Transactions Query
`GET /api/v1/transactions/`
- **Query Parameters**:
  - `search`: Keyword search in description, merchant name, notes.
  - `category_id`: Filter by specific category UUID.
  - `merchant_name`: Filter by merchant.
  - `transaction_type`: `debit`, `credit`, or `transfer`.
  - `payment_method`: Filter by payment mode.
  - `source`: Filter by data ingestion source.
  - `start_date` / `end_date`: Date range filters (`YYYY-MM-DD`).
  - `min_amount` / `max_amount`: Numeric range filters.
  - `sort_by`: `transaction_date`, `amount`, `merchant_name`, `created_at`.
  - `sort_order`: `desc` or `asc`.
  - `page`: 1-indexed page number (default `1`).
  - `page_size`: Items per page (default `20`, max `100`).
- **Response**:
```json
{
  "items": [...],
  "total_count": 142,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

### 2. Manual Transaction Creation
`POST /api/v1/transactions/`
- **Payload**: Full `TransactionCreate` schema with amount validation (`amount > 0`).

### 3. Get Single Transaction
`GET /api/v1/transactions/{id}`
- Returns transaction details with joined category and metadata. Prevents IDOR (returns 404 for other users).

### 4. Update Transaction
`PUT /api/v1/transactions/{id}`
- Updates mutable fields (`amount`, `merchant_name`, `category_id`, `subcategory`, `payment_method`, `notes`, etc.).

### 5. Delete Transaction
`DELETE /api/v1/transactions/{id}`
- Removes transaction with authorization verification.

---

## Frontend Capabilities
- **Multi-Filter Bar**: Real-time search with debounce, transaction type toggles (`All`, `Debit`, `Credit`), collapsible advanced filters for date ranges, amount bounds, category dropdown, payment methods, and ingestion sources.
- **Database-Level Pagination**: Server-side page navigation and page size selector (`10`, `20`, `50`), minimizing client memory consumption.
- **Interactive Modals**:
  - **Record Transaction**: Validates positive amounts, currency picker, category selector, payment method dropdown, and custom subcategory.
  - **Edit Transaction**: Pre-fills existing data for instant updates.
  - **Transaction Details**: Detailed view with category color badges, confidence score meter, and timestamp audit info.
