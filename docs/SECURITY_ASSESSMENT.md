# FinSight AI — Security & Privacy Assessment

---

## 1. Threat Model & Mitigations

| Threat Vector | Risk Level | System Safeguard |
|---------------|------------|-------------------|
| **PII in Uploaded Documents** | Critical | Local regular expression & NER privacy scrubber masks PAN cards, Aadhaar, bank account numbers, credit cards, emails, and phone numbers before storage and AI synthesis. |
| **Credential Hijacking** | High | Password hashing via `bcrypt` with automatic salting; short-lived JSON Web Tokens (JWT) signed with HMAC-SHA256. |
| **SQL Injection** | High | Parameterized queries enforced across all database queries via SQLAlchemy 2.0 ORM. |
| **Insecure Direct Object Reference (IDOR)** | High | Every database query explicitly filters by the authenticated user's `current_user.id`. |
| **Cross-Origin Resource Sharing (CORS)** | Medium | Strict whitelist of permitted origin URLs with controlled header access. |

---

## 2. PII Redaction Verification

The built-in `PIIScrubber` scans raw OCR text and document streams:
- **Card Patterns:** `\b(?:\d{4}[-\s]?){3}\d{4}\b` $\to$ `[REDACTED_CARD]`
- **PAN Patterns:** `\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b` $\to$ `[REDACTED_PAN]`
- **Aadhaar Patterns:** `\b\d{4}\s\d{4}\s\d{4}\b` $\to$ `[REDACTED_AADHAAR]`
- **Email Patterns:** Masked to `[REDACTED_EMAIL]`
- **Phone Patterns:** Masked to `[REDACTED_PHONE]`
