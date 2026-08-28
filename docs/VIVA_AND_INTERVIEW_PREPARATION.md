# FinSight AI — Technical Viva & Interview Preparation Guide

---

## 1. 10-Minute Comprehensive Demo Script

```
[00:00 - 01:30] Executive Overview & Problem Statement
"Good morning/afternoon. Today I am presenting FinSight AI, a production-grade enterprise fintech platform built to solve personal wealth management challenges. Most financial apps suffer from fragmented data sources, weak categorization, and AI tools that hallucinate math. FinSight AI addresses this through multi-source ingestion, a 4-layer ML categorizer, local PII privacy scrubbing, deterministic financial calculation guardrails, and grounded multi-agent AI."

[01:30 - 03:30] Multi-Source Ingestion & Local PII Protection
"Let's navigate to /upload. We support Indian bank statements (HDFC PDF, SBI CSV), UPI exports (PhonePe), and image receipts. Watch as I upload a receipt:
1. Magic bytes validation checks the file signature (%PDF, PNG, JPEG).
2. Local PII Scrubber redacts PAN numbers, Aadhaar, and credit card numbers before any data leaves the device or enters AI context.
3. Tesseract OCR layout parsing extracts total amount, date, and candidate merchant.
4. The system presents candidate transactions for single-click confirmation to the user ledger."

[03:30 - 05:30] Dashboard & Composite Financial Health Score
"Navigating to /dashboard, we see our financial metrics. Our Composite Financial Health Score (0-100) is calculated deterministically across 7 factor bars: Savings Rate, Emergency Fund, Debt Ratio, Expense-to-Income, Budget Discipline, Investment Allocation, and Cash Runway. Notice how these numbers update instantly in real-time."

[05:30 - 07:30] Machine Learning, Anomaly Detection & Forecasting
"Under /analytics and /forecast:
1. Expense Categorization operates via a 4-layer pipeline (User Rules -> Keyword Regex -> TF-IDF Logistic Regression ML -> User Feedback Learning).
2. Anomaly Detection flags spending surges, amount outliers (Z > 3.0σ), frequency bursts, and subscription hikes.
3. Time-Series Forecasting projects 30/60/90-day expenses using Holt's exponential smoothing with explicit non-guaranteed disclaimers."

[07:30 - 09:30] Grounded AI Advisor & Multi-Guru Personas
"On /advisor and /philosophies:
1. The AI Financial Advisor uses a LangGraph agent. Notice that when I ask 'How long to reach my ₹10L goal?', the LLM NEVER calculates the money. It invokes our deterministic Python calculate_sip tool to return exact maturity schedules.
2. RAG Retrieval searches indexed finance literature (The Psychology of Money, Rich Dad Poor Dad, Ramit Sethi) with page-backed citations.
3. Multi-Guru comparison presents advice side-by-side from Warren Buffett, Robert Kiyosaki, Ramit Sethi, and an Indian Wealth Advisor."

[09:30 - 10:00] Summary & Closing
"FinSight AI is validated with 106 automated tests, sub-35ms query latency at 100,000 transactions, 100% safety compliance, and Next.js SSR production builds. Thank you, I am ready for your questions."
```

---

## 2. 5-Minute High-Impact Demo Script

```
[00:00 - 01:00] Pitch & Ingestion
"FinSight AI is a full-stack AI fintech platform that converts unstructured bank statements and receipts into actionable wealth intelligence. Let's upload an HDFC statement on /upload. Our adapter parses transaction candidates while the Local PII Scrubber redacts sensitive PAN and Aadhaar details."

[01:00 - 02:15] Financial Health & What-If Simulator
"On /dashboard, our 0-100 Financial Health Score assesses cash flow and emergency reserves deterministically. On /simulator, adjusting slider inputs recalculates monthly cash flow and goal target acceleration instantly without LLM hallucinations."

[02:15 - 04:00] Grounded AI Advisor & Multi-Guru Comparison
"On /advisor, our LangGraph Agent invokes Python calculation tools for SIP and loan EMI schedules, backing responses with page-level citations from financial literature (The Psychology of Money). On /philosophies, users compare advice across Warren Buffett, Robert Kiyosaki, and Ramit Sethi."

[04:00 - 05:00] Verification & Wrap-up
"Supported by a 106-test suite, 100k transaction scale benchmarking, and production Docker containerization. Thank you."
```

---

## 3–16. System Component Technical Explanations

### 3. System Architecture
"FinSight AI is structured as a decoupled multi-tier system: Next.js 14 App Router frontend communicating over REST API to a FastAPI ASGI gateway backend, backed by Managed PostgreSQL with `pgvector` for relational and semantic vector storage."

### 4. Database Architecture
"Utilizes SQLAlchemy 2.0 Async ORM with a normalized relational schema. Indexed with multi-column composite indices (`user_id`, `is_deleted`, `transaction_date`) for sub-35ms query times at 100,000 transactions."

### 5. OCR Pipeline
"Magic byte validation verifies binary signatures (`%PDF`, `PNG`, `JPEG`) before saving. OpenCV and PIL apply binarization and deskewing, followed by Tesseract OCR layout parsing to generate confirmed candidates."

### 6. Expense Categorization Engine
"Implements a 4-layer fallback pipeline: Layer 1 User Rules $\to$ Layer 2 Keyword Regex $\to$ Layer 3 Scikit-learn TF-IDF Logistic Regression ML $\to$ Layer 4 Low Confidence Flag & User Learning."

### 7. Machine Learning Infrastructure
"Employs TF-IDF feature extraction with Multinomial Logistic Regression trained on Indian payment data, achieving high generalization for UPI and merchant strings."

### 8. LangGraph AI Agent Architecture
"Features a stateful LangGraph agent that orchestrates tool calling. The LLM acts purely as an intent classifier and natural language synthesizer, while calculations run in Python."

### 9. RAG Literature Architecture
"Indexes top personal finance books using 500-token page-aware chunking (50-token overlap). Embeddings are queried via cosine similarity with a 0.65 relevance threshold filter."

### 10. Financial Health Score Engine
"Computes a 0–100 composite score based on 7 weighted factors: Savings Rate (20%), Emergency Fund (20%), Debt Ratio (15%), Expense Ratio (15%), Budget Adherence (10%), Investment Rate (10%), and Cash Runway (10%)."

### 11. Anomaly Detection Engine
"Flags anomalies across 5 dimensions: category spending surges, transaction amount z-scores ($Z > 3.0\sigma$), merchant spikes, frequency bursts, and subscription price hikes (> 10%)."

### 12. Expense Forecasting Engine
"Uses Holt's exponential smoothing for 30/60/90-day time-series projections, backtested against holdout historical data and guarded with non-guaranteed financial disclaimers."

### 13. Security Architecture
"Defense-in-depth security: local PII scrubbing (PAN, Aadhaar, cards), thread-safe JWT token revocation, CORS origin whitelisting, IP rate limiting, and security headers (HSTS, CSP)."

### 14. Deployment Architecture
"Docker Compose composition featuring PostgreSQL 16 `pgvector`, FastAPI Uvicorn ASGI backend, Next.js static asset compilation, and Nginx reverse proxy with SSL/TLS termination."

### 15. Performance Benchmarks
"Benchmarked at 10k, 50k, and 100k transaction scale. Database composite indexes and SQL `func.sum()` aggregations keep queries < 35ms and dashboard loads < 85ms."

### 16. AI Evaluation Framework
"Evaluates agent responses across 8 pillars (calculation correctness, tool accuracy, RAG relevance, groundedness, hallucination rate, advice usefulness, safety compliance, consistency) using deterministic fact assertions."

---

## 17. 30 Difficult Viva Questions & Technical Answers

#### Q1: Why FastAPI over Django or Flask?
**Answer**: FastAPI provides native async/await performance on Uvicorn ASGI, built-in Pydantic v2 data validation, dynamic OpenAPI documentation generation, and high throughput for async database queries with SQLAlchemy 2.0.

#### Q2: Why PostgreSQL instead of MongoDB or SQLite?
**Answer**: PostgreSQL provides ACID transaction guarantees required for financial ledgers, robust multi-column indexing, and native `pgvector` support for RAG semantic search without needing a separate vector database cluster.

#### Q3: Why LangGraph for the AI Agent?
**Answer**: LangGraph provides explicit state-machine control, cyclic execution graphs, deterministic tool binding, and robust state persistence, avoiding un-bounded LLM loops.

#### Q4: Why RAG instead of fine-tuning an LLM?
**Answer**: RAG allows real-time dynamic context update, eliminates knowledge staleness, prevents hallucinated book quotes, and provides exact page-aware citations (`[Psychology of Money, Page 42]`).

#### Q5: Why prohibit the LLM from calculating financial math?
**Answer**: LLMs are probabilistic token predictors and inherently unreliable at floating-point arithmetic. All numerical calculations (SIP, EMI, Emergency Fund) run in deterministic Python functions.

#### Q6: How is multi-tenant user isolation enforced?
**Answer**: Every repository query enforces explicit `user_id == current_user.id` filters in SQLAlchemy. IDOR tests verify cross-tenant access attempts return HTTP 403/404.

#### Q7: How does OCR fallback work if Tesseract fails?
**Answer**: If Tesseract OCR confidence drops below 60%, candidate transactions are flagged as `unverified` and routed to the manual review queue, preserving ledger integrity.

#### Q8: How is the expense categorization ML model evaluated?
**Answer**: Evaluated via precision, recall, F1-score, and confusion matrix across a 20% holdout test set, requiring F1-score > 0.85 before model updates.

#### Q9: How do you detect LLM hallucinations?
**Answer**: Via our AI Evaluation Framework: regex extraction checks output numbers against deterministic Python tool outputs. If a response contains un-sourced numbers, hallucination rate increases.

#### Q10: How do you handle conflicting financial philosophies (e.g., Kiyosaki vs. Sethi)?
**Answer**: They are intentionally presented side-by-side in separate persona response objects so users can compare real estate leverage (Kiyosaki) vs. conscious spending (Sethi) transparently.

#### Q11: How do you protect financial data privacy?
**Answer**: Local PII Scrubber redacts PAN, Aadhaar, credit card numbers, and emails using regex before data hits logs, database, or LLM context windows.

#### Q12: How does expense forecasting handle seasonal spikes (e.g., Diwali / Holidays)?
**Answer**: Uses Holt's exponential smoothing with trend components, while anomaly detector flags seasonal spikes as expected bursts rather than model drift.

#### Q13: How does anomaly detection prevent false positives on new accounts?
**Answer**: Minimum history guardrail: requires at least 15 historical transactions or 30 days of data before triggering surge alarms.

#### Q14: How are JWT tokens invalidated upon logout?
**Answer**: Revoked token IDs are stored in a thread-safe `_REVOKED_TOKENS` set guarded by `threading.Lock()`. Middleware checks token IDs against this blacklist.

#### Q15: What is the purpose of magic bytes validation?
**Answer**: Prevents malicious file upload attacks (e.g., executable hidden in .pdf extension) by inspecting file header bytes (`%PDF`, `\x89PNG`) before saving to disk.

#### Q16: How does the What-If Simulator calculate goal acceleration?
**Answer**: Deterministic compound interest formula $A = P(1 + r/n)^{nt} + PMT \times \frac{(1 + r/n)^{nt} - 1}{r/n}$ comparing base vs. simulated monthly contribution.

#### Q17: What database indexes were added for performance?
**Answer**: Composite indexes `ix_transactions_user_active_date` (`user_id`, `is_deleted`, `transaction_date`) and `ix_transactions_user_active_type_date`.

#### Q18: How is rate limiting implemented?
**Answer**: Token bucket rate-limiting middleware tracking client IP address (`request.client.host`) in `backend/app/main.py` returning HTTP 429 on limit breaches.

#### Q19: Why use Vanilla CSS instead of heavy UI libraries?
**Answer**: Vanilla CSS custom properties ensure zero runtime overhead, exact design token control, smooth 60fps animations, and light bundle sizes.

#### Q20: How are PDF reports generated in the backend?
**Answer**: Using ReportLab PDF engine: deterministically formats 11 financial report sections, category tables, and disclaimer footers into downloadable binary streams.

#### Q21: How do bank statement adapters handle different formats?
**Answer**: Poly-adapter pattern: HDFC PDF parser uses layout coordinates, SBI CSV adapter maps column headers, and PhonePe parser extracts UPI ref IDs.

#### Q22: What happens if a database transaction fails during CSV import?
**Answer**: Async session context manager executes `await db.rollback()`, ensuring partial imports leave zero orphan transactions in the database.

#### Q23: How do you benchmark system latency under load?
**Answer**: `tests/test_performance_benchmark.py` populates synthetic ledgers (10k, 50k, 100k rows) and measures execution time for queries, aggregations, and health score calculations.

#### Q24: How are recurring subscriptions identified?
**Answer**: Merchant frequency heuristic: analyzes normalized merchant names appearing on recurring calendar intervals ($\pm 3$ days for monthly, $\pm 10$ days for annual).

#### Q25: Why return an error_id UUID in sanitized 500 error responses?
**Answer**: Prevents internal stack trace leakage to clients while allowing engineers to correlate client errors with server-side log entries.

#### Q26: What is the cosine relevance threshold in RAG?
**Answer**: Threshold set to 0.65: vector chunks with similarity score < 0.65 are discarded to prevent injecting irrelevant context into LLM prompts.

#### Q27: How is PII scrubber performance optimized?
**Answer**: Compiled regex patterns stored as module-level constants run in linear time $O(N)$ over input character length.

#### Q28: How does Next.js 14 App Router improve frontend performance?
**Answer**: Enables Server-Side Rendering (SSR), static page generation (19 pre-rendered routes), automatic code splitting, and optimized bundle delivery.

#### Q29: How does the system comply with GDPR data deletion?
**Answer**: Account deletion unlinks physical upload files from disk (`os.remove()`) before executing cascading SQL deletes on user records.

#### Q30: What is the primary engineering achievement of FinSight AI?
**Answer**: Architecting a enterprise fintech system that pairs strict deterministic financial math with grounded multi-agent AI and sub-35ms high-scale database queries.
