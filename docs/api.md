# FinSight AI — API Specification & Integration Reference

## Overview
The FinSight AI REST API is built on FastAPI, offering OpenAPI v3 interactive documentation, JSON payload contracts, and JWT Bearer token authentication.

Base Path: `/api/v1`

---

## Authentication & Authorization (`/api/v1/auth`)

| Endpoint | Method | Description | Security |
|---|---|---|---|
| `/auth/register` | `POST` | Create a new user account | Public |
| `/auth/login` | `POST` | Authenticate user and receive JWT access token | Public |
| `/auth/logout` | `POST` | Revoke JWT token and destroy session | Bearer Token |
| `/auth/me` | `GET` | Fetch authenticated user profile & settings | Bearer Token |

---

## Transactions API (`/api/v1/transactions`)

| Endpoint | Method | Description | Security |
|---|---|---|---|
| `/transactions/` | `GET` | List transactions with filtering, search & pagination | Bearer Token |
| `/transactions/` | `POST` | Create a manual transaction record | Bearer Token |
| `/transactions/{id}` | `GET` | Fetch transaction details by ID | Bearer Token |
| `/transactions/{id}` | `PUT` | Update transaction details or category | Bearer Token |
| `/transactions/{id}` | `DELETE` | Soft-delete transaction record | Bearer Token |

---

## Financial Analytics & Health (`/api/v1/analytics`)

| Endpoint | Method | Description | Security |
|---|---|---|---|
| `/analytics/summary` | `GET` | Monthly income, expense, net cash flow & savings rate | Bearer Token |
| `/analytics/category-split` | `GET` | Needs / Wants / Savings 50/30/20 category split | Bearer Token |
| `/analytics/top-merchants` | `GET` | Top merchants by total expenditure | Bearer Token |
| `/analytics/health-score` | `GET` | Composite 0–100 Financial Health Score & 7 factor bars | Bearer Token |
| `/analytics/simulate` | `POST` | Deterministic What-If Financial Scenario Simulator | Bearer Token |

---

## Document Ingestion & OCR (`/api/v1/documents`)

| Endpoint | Method | Description | Security |
|---|---|---|---|
| `/documents/upload/receipt` | `POST` | Upload receipt image for OCR processing | Bearer Token |
| `/documents/upload/bank-statement` | `POST` | Ingest CSV or PDF bank statement | Bearer Token |
| `/documents/{doc_id}/confirm` | `POST` | Confirm OCR candidates into permanent ledger | Bearer Token |

---

## AI Advisor & Philosophy (`/api/v1/advisor`)

| Endpoint | Method | Description | Security |
|---|---|---|---|
| `/advisor/chat` | `POST` | Send message to AI Advisor with grounded tool execution | Bearer Token |
| `/advisor/gurus/compare` | `POST` | Compare financial question across 4 guru personas | Bearer Token |
| `/reports/monthly` | `GET` | Generate 11-section deterministic financial report | Bearer Token |
| `/reports/monthly/pdf` | `GET` | Export monthly financial report as PDF document | Bearer Token |
