# FinSight AI — Security Architecture & Threat Model

**Version:** 1.0.0  
**Classification:** Fintech Confidential  
**Authentication Standard:** JWT (HMAC-SHA256) with Bcrypt Password Hashing  
**Privacy Compliance:** GDPR / Right-to-be-Forgotten & Local PII Scrubbing

---

## 1. Authentication & Token Lifecycle

```
┌─────────────────────────────────┐
│        NEXT.JS FRONTEND         │
└────────────────┬────────────────┘
                 │ 1. POST /api/v1/auth/login (email + password)
                 ▼
┌─────────────────────────────────┐
│       FASTAPI AUTH SERVICE      │
│  - Verify bcrypt password       │
│  - Generate JWT access token    │
│  - Issue user claims (sub=UUID) │
└────────────────┬────────────────┘
                 │ 2. Return JWT Bearer Token
                 ▼
┌─────────────────────────────────┐
│     AUTHENTICATED REQUESTS      │
│ Authorization: Bearer <JWT>     │
│  - Token expiration validated   │
│  - Revocation blacklist checked │
│  - User ownership enforced      │
└─────────────────────────────────┘
```

### 1.1 Password Security & Hashing
- Passwords are encrypted using **Bcrypt** with an adaptive work factor (12 rounds).
- Raw passwords are never logged, persisted in plaintext, or transmitted across unsecured channels.
- Registration enforces a minimum password length of 8 characters.

### 1.2 JWT Token Architecture
- **Algorithm:** HMAC-SHA256 (`HS256`).
- **Secret Key:** Injected via environment variable `SECRET_KEY`. Zero hardcoded secrets in source code.
- **Expiration:** Configured via `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60 minutes).
- **Claims:**
  - `sub`: User UUID identifier.
  - `exp`: Expiration timestamp in UTC.
  - `iat`: Issued-at timestamp in UTC.
  - `type`: `access`.

### 1.3 Token Revocation & Logout
- When a user logs out (`POST /api/v1/auth/logout`), the token signature is immediately blacklisted in the revocation store.
- Any subsequent API requests using a revoked token are rejected with `401 Unauthorized`.

---

## 2. Authorization & Insecure Direct Object Reference (IDOR) Defense

Every private financial entity (`Transaction`, `Budget`, `FinancialGoal`, `FinancialDocument`, `Subscription`, `Anomaly`) strictly verifies user ownership in the data access and service layer:

```python
# Guaranteed User Isolation Pattern
res = await db.execute(
    select(Transaction).filter(
        Transaction.id == tx_id,
        Transaction.user_id == current_user.id # Strict ownership clause
    )
)
```

- **Cross-User Data Access Prevention:**
  - Attempting to view another user's transaction $\to$ `404 Not Found`.
  - Attempting to update another user's budget $\to$ `404 Not Found`.
  - Attempting to view or delete another user's document $\to$ `404 Not Found`.
  - Information leakage is prevented by returning generic `404 Not Found` rather than `403 Forbidden`.

---

## 3. Privacy, PII Redaction & Data Deletion

1. **Local PII Scrubber (`backend/app/core/pii_scrubber.py`):**
   - Automatically sanitizes PAN numbers, Aadhaar numbers, 16-digit credit card numbers, bank account numbers, email addresses, and phone numbers before storing OCR extractions.
2. **Right to be Forgotten (`DELETE /api/v1/auth/me`):**
   - Enables users to request permanent deletion of their account and all associated financial records, documents, goals, and credentials.
   - Revokes active sessions and logs a final anonymized GDPR audit event.

---

## 4. Security Verification & Test Suite

The security layer is verified via automated tests in `tests/test_security_and_auth.py`:
- `test_unauthorized_requests`: All endpoints reject unauthenticated calls with `401`.
- `test_invalid_and_expired_tokens`: Expired or signature-tampered tokens fail with `401`.
- `test_logout_and_token_revocation`: Revoked tokens are rejected on subsequent requests.
- `test_idor_transaction_access_prevention`: Prevents unauthorized read/write/delete across users.
- `test_idor_budget_and_document_prevention`: Enforces strict isolation on financial documents and budgets.
- `test_user_preferences_and_privacy_deletion`: Verifies preference updates and GDPR data erasure.
