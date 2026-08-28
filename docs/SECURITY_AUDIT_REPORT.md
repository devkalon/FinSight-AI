# FinSight AI — Comprehensive Security Audit Report

## Executive Summary
A full security audit was conducted on the FinSight AI platform across backend architecture, authentication, authorization, multi-tenant isolation, file ingestion, deterministic engines, and API endpoints. 

Overall, the core architecture enforces strong security foundations:
- **Zero Raw SQL Injection**: Parameterized SQLAlchemy ORM queries are utilized across all modules.
- **Strict User Isolation**: All transactional, budget, goal, subscription, and document queries enforce `user_id == current_user.id` filters, preventing Insecure Direct Object Reference (IDOR) vulnerabilities.
- **PII Scrubbing Layer**: Indian PAN, Aadhaar, credit card numbers, CVVs, and account numbers are scrubbed before ML/OCR and LLM processing.
- **Prompt Injection & LLM Isolation**: The AI Advisor and RAG engine do not execute dynamic code or raw queries; all financial calculations are executed by deterministic backend Python functions.

Below is the detailed categorization of security findings across **CRITICAL**, **HIGH**, **MEDIUM**, and **LOW** severities with recommended remediations.

---

## Findings by Severity

```
┌─────────────────────────┬──────────┬────────────────────────────────────────────────────────┐
│ Vulnerability ID        │ Severity │ Summary                                                │
├─────────────────────────┼──────────┼────────────────────────────────────────────────────────┤
│ SEC-01                  │ CRITICAL │ Hardcoded Default Secret Key Fallback for JWT Signing  │
│ SEC-02                  │ CRITICAL │ Permissive Wildcard CORS with Credentials Allowed      │
│ SEC-03                  │ HIGH     │ Missing Rate Limiting on Auth, Ingestion & AI Endpoints│
│ SEC-04                  │ HIGH     │ In-Memory Token Revocation Store in Multi-Worker Env   │
│ SEC-05                  │ MEDIUM   │ Unlinked File Residuals on GDPR User Account Deletion  │
│ SEC-06                  │ MEDIUM   │ File Validation Relies on Extension rather than Magic  │
│ SEC-07                  │ LOW      │ Verbose Error Traces in Unhandled Exceptions           │
│ SEC-08                  │ LOW      │ Missing Standard HTTP Security Headers (CSP, HSTS)     │
└─────────────────────────┴──────────┴────────────────────────────────────────────────────────┘
```

---

### 1. CRITICAL SEVERITY

#### SEC-01: Hardcoded Default Secret Key Fallback for JWT Signing
- **Vulnerability**: In `backend/app/core/config.py`, `SECRET_KEY` falls back to `"super-secret-finsight-ai-jwt-key-2026-secure-token-vault"` if not defined in the environment.
- **Affected Files**:
  - [`backend/app/core/config.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/core/config.py#L8)
- **Impact**: If deployed to staging or production without setting `SECRET_KEY` in `.env`, an attacker could forge arbitrary JWT tokens with any `sub` (user_id), gaining full unauthorized access to any user account and financial ledger.
- **Recommended Fix**:
  - Raise an explicit `ValueError` on startup if `SECRET_KEY` is missing or matches the default development key when running in production (`ENVIRONMENT=production`).

---

#### SEC-02: Permissive Wildcard CORS Configuration with Credentials
- **Vulnerability**: In `backend/app/core/config.py` and `backend/app/main.py`, `BACKEND_CORS_ORIGINS` contains `"*"` alongside `allow_credentials=True`.
- **Affected Files**:
  - [`backend/app/core/config.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/core/config.py#L16-L22)
  - [`backend/app/main.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/main.py#L21-L28)
- **Impact**: While modern browsers disallow wildcard origins when credentials are included, this configuration can cause CORS misconfigurations or allow malicious websites to initiate cross-origin requests that leak sensitive financial data.
- **Recommended Fix**:
  - Remove `"*"` from `BACKEND_CORS_ORIGINS`.
  - Whitelist only trusted frontend origins: `http://localhost:3000`, `http://127.0.0.1:3000`, and authorized production domain URLs.

---

### 2. HIGH SEVERITY

#### SEC-03: Missing Rate Limiting on Auth, Ingestion & AI Endpoints
- **Vulnerability**: Sensitive API endpoints lack rate limiting (e.g., SlowAPI / Redis token bucket).
- **Affected Files**:
  - [`backend/app/api/v1/endpoints/auth.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/api/v1/endpoints/auth.py) (`/login`, `/register`)
  - [`backend/app/api/v1/endpoints/documents.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/api/v1/endpoints/documents.py) (`/upload/receipt`, `/upload/bank-statement`)
  - [`backend/app/api/v1/endpoints/advisor.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/api/v1/endpoints/advisor.py) (`/chat`)
- **Impact**: Enables credential brute-forcing, denial-of-service, or compute exhaustion on computationally heavy OCR and ML inference tasks.
- **Recommended Fix**:
  - Introduce `slowapi` middleware (e.g. 5 requests/minute for login, 15 requests/minute for OCR uploads, 30 requests/minute for advisor chat).

---

#### SEC-04: In-Memory Token Revocation Store in Multi-Worker Environments
- **Vulnerability**: In `backend/app/core/security.py`, `revoke_token()` stores invalidated JWTs in a local in-memory Python `set` (`_REVOKED_TOKENS`).
- **Affected Files**:
  - [`backend/app/core/security.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/core/security.py)
- **Impact**: In multi-process ASGI deployments (`uvicorn --workers 4`) or horizontally scaled container clusters, a token revoked on one worker process remains valid on other workers until natural expiration.
- **Recommended Fix**:
  - Store revoked tokens (or user revocation timestamp checkpoints) in a shared Redis cache or a lightweight `revoked_tokens` database table with TTL.

---

### 3. MEDIUM SEVERITY

#### SEC-05: Unlinked File Residuals on GDPR User Account Deletion
- **Vulnerability**: In `backend/app/services/auth_service.py` (`delete_user_data`), user database rows are deleted, but physical binary files saved in `uploads/receipts/` and `uploads/statements/` remain on disk.
- **Affected Files**:
  - [`backend/app/services/auth_service.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/services/auth_service.py#L186-L208)
- **Impact**: Residual financial statement PDFs and receipt images containing customer transactions remain stored in server disk storage, falling short of strict GDPR Article 17 "Right to Erasure" requirements.
- **Recommended Fix**:
  - Unlink all physical file paths referenced by the user's `FinancialDocument` records before executing database deletion.

---

#### SEC-06: File Validation Relies Solely on Extension Rather than Magic Bytes
- **Vulnerability**: In `backend/app/services/ingestion/document_service.py`, file validation checks `ALLOWED_IMAGE_EXTENSIONS` based on filename extensions (`.jpg`, `.png`, `.pdf`, `.csv`) without inspecting magic byte headers.
- **Affected Files**:
  - [`backend/app/services/ingestion/document_service.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/services/ingestion/document_service.py#L21-L24)
- **Impact**: Potential upload of polyglot or non-image payloads disguised with image extensions.
- **Recommended Fix**:
  - Inspect file byte signatures (`b'%PDF'` for PDFs, `b'\x89PNG'` for PNGs, `b'\xff\xd8\xff'` for JPEGs) in addition to extension filtering.

---

### 4. LOW SEVERITY

#### SEC-07: Verbose Error Details in Unhandled Exceptions
- **Vulnerability**: Unhandled 500 errors could expose internal stack traces or library version numbers.
- **Affected Files**:
  - [`backend/app/main.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/main.py)
- **Impact**: Low-level information disclosure.
- **Recommended Fix**:
  - Add a generic global exception handler that logs full tracebacks to server logs while returning a structured error response with an incident tracking ID.

---

#### SEC-08: Missing Standard HTTP Security Headers (CSP, HSTS)
- **Vulnerability**: Response headers do not include standard defense-in-depth headers such as `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, or `Content-Security-Policy`.
- **Affected Files**:
  - [`backend/app/main.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/main.py)
- **Impact**: Potential exposure to clickjacking or MIME-type sniffing in legacy clients.
- **Recommended Fix**:
  - Add security header middleware to inject standard security headers on all API responses.

---

## Next Steps
In accordance with Rule 10 of `For Me.txt`, **no code modifications have been made initially**. 

Please review this security audit report and let me know if you would like me to proceed with implementing these remediations.
