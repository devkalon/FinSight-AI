# FinSight AI — Security Architecture & Hardening Controls

## Overview
FinSight AI implements defense-in-depth security controls across authentication, authorization, file upload handling, rate limiting, and PII protection.

---

## Remediated Vulnerabilities & Defense Matrix

| Control ID | Risk Domain | Implemented Remediation | Verification |
|---|---|---|---|
| **SEC-01** | Secrets & Auth | Production validation in `backend/app/core/config.py` rejecting default JWT secret keys | `test_sec01_production_secret_validation` |
| **SEC-02** | CORS Policy | Whitelisted CORS origins removing `"*"` wildcards in `backend/app/core/config.py` | `test_sec02_cors_wildcard_remover` |
| **SEC-03** | Rate Limiting | IP token bucket rate limiting middleware in `backend/app/main.py` | `test_sec03_rate_limiting_middleware` |
| **SEC-04** | Session Management | Thread-safe `threading.Lock()` token revocation tracking | `test_sec04_thread_safe_token_revocation` |
| **SEC-05** | GDPR & Deletion | Physical disk file unlinking before database deletion on GDPR account removal | `test_user_preferences_and_privacy_deletion` |
| **SEC-06** | File Upload Security | Magic byte header validation (`%PDF`, `\x89PNG`, `\xff\xd8\xff`, `RIFF...WEBP`, `BM`, UTF-8 text for CSVs) | `test_sec06_magic_bytes_file_upload_validation` |
| **SEC-07** | Error Exposure | Global exception handler returning sanitized JSON 500 responses with `error_id` UUID | `test_health_endpoints` |
| **SEC-08** | Response Headers | Security response headers (`HSTS`, `CSP`, `X-Frame-Options`, `X-Content-Type-Options`) | `test_sec08_security_response_headers` |

---

## Local PII Scrubber Mechanics

The PII Scrubber ([`backend/app/core/pii_scrubber.py`](file:///c:/Users/devKalon/Desktop/Capabl/backend/app/core/pii_scrubber.py)) executes regex redaction before text persistence or AI prompt assembly:

- **PAN Card**: `[A-Z]{5}[0-9]{4}[A-Z]{1}` $\to$ `[REDACTED_PAN]`
- **Aadhaar Number**: `\b\d{4}\s?\d{4}\s?\d{4}\b` $\to$ `[REDACTED_AADHAAR]`
- **Credit/Debit Card**: `\b(?:\d[ -]*?){13,16}\b` $\to$ `[REDACTED_CARD]`
- **Email Address**: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b` $\to$ `[REDACTED_EMAIL]`
- **Phone Number**: `\b(?:\+91|0)?[6-9]\d{9}\b` $\to$ `[REDACTED_PHONE]`
