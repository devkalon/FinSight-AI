<p align="center">
  <img src="logo.png" alt="FinSight AI" width="420" />
</p>

<p align="center">
  <strong>Insights Today. Wealth Tomorrow.</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#api-reference">API</a> •
  <a href="#testing">Testing</a> •
  <a href="#credits">Credits</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-AI_Agent-FF6F00?style=for-the-badge&logo=chainlink&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

---

## What is FinSight AI?

**FinSight AI** is a full-stack, AI-powered personal finance and wealth management platform built for the Indian financial ecosystem. It combines intelligent document ingestion, ML-driven analytics, and an agentic AI advisor to give users complete visibility and control over their financial life.

Upload a bank statement PDF, a UPI receipt screenshot, or a CSV export — FinSight automatically extracts transactions, categorizes spending, detects anomalies, tracks subscriptions, and delivers actionable insights through an interactive AI advisor that speaks the language of legendary financial thinkers.

---

## Features

### 📄 Intelligent Document Ingestion
- **Multi-format support** — PDF bank statements, receipt images (OCR), and CSV exports
- **Indian bank adapters** — Pre-built parsers for HDFC, ICICI, SBI, and UPI transaction formats
- **OCR pipeline** — Tesseract + Pillow preprocessing with EXIF correction, DPI scaling, and adaptive thresholding
- **Indian financial normalization** — ₹ currency parsing, lakh/crore notation, UPI reference extraction

### 🤖 Agentic AI Financial Advisor
- **LangGraph-powered ReAct agent** — Tool-calling architecture with structured financial reasoning
- **RAG knowledge engine** — Retrieval-augmented generation grounded in the user's own financial data
- **Multi-philosophy comparison** — Compare advice from Warren Buffett (value compounding), Robert Kiyosaki (cashflow assets), and Ramit Sethi (conscious spending)
- **Financial guru personas** — Each guru has a distinct personality, vocabulary, and investment philosophy
- **Red team evaluation** — Automated adversarial testing for AI safety and grounding validation

### 📊 ML Analytics Engine
- **Smart categorization** — Rule-based + ML hybrid categorizer with merchant learning and 50/30/20 budget classification
- **Expense forecasting** — Time-series prediction using linear regression with seasonal adjustments
- **Anomaly detection** — Six-strategy detector (statistical outliers, frequency anomalies, merchant spikes, round-number detection, weekend/holiday patterns, category drift)
- **Subscription tracker** — Automatic recurring payment detection with billing cycle inference

### 💰 Financial Health & Planning
- **Financial Health Score** — Composite 0–100 score across savings rate, debt-to-income, emergency fund, expense stability, and investment diversity
- **Budget management** — Category-level budgets with real-time tracking, alerts, and rollover support
- **Financial goals** — Goal creation with milestone tracking, contribution logging, and progress visualization
- **What-If simulator** — Scenario modeling for salary changes, new expenses, investment returns, and debt payoff

### 📈 Reports & Visualization
- **Interactive dashboard** — Real-time spending charts, income vs. expense trends, and category breakdowns (Recharts)
- **Monthly financial reports** — Auto-generated PDF reports with charts, insights, and recommendations (ReportLab)
- **Trend analytics** — Month-over-month comparisons, top merchants, spending velocity analysis

### 🔒 Security & Privacy
- **JWT authentication** — Secure token-based auth with bcrypt password hashing
- **Google OAuth 2.0** — One-click sign-in with automatic profile provisioning
- **Token revocation** — Thread-safe in-memory revocation store with logout support
- **GDPR account deletion** — Full data purge including uploaded documents and audit trails
- **Audit logging** — Every sensitive operation is recorded with user ID, action type, and timestamp
- **Input validation** — Pydantic v2 schemas for strict request/response validation throughout

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | Async Python API framework |
| **SQLAlchemy 2.0** | Async ORM with full relationship mapping |
| **PostgreSQL 16 + pgvector** | Relational data store with vector embedding support |
| **Alembic** | Database migrations |
| **LangGraph + LangChain** | Agentic AI orchestration and tool-calling |
| **scikit-learn** | ML models for categorization, forecasting, anomaly detection |
| **Pillow + Tesseract** | Image preprocessing and OCR |
| **pypdf + pdfplumber** | PDF text extraction |
| **ReportLab** | PDF report generation |
| **pandas + NumPy** | Data wrangling and numerical computation |

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 14** | React framework with App Router |
| **TypeScript** | Type-safe frontend development |
| **Tailwind CSS** | Utility-first styling |
| **Recharts** | Interactive financial charts and visualizations |
| **Lucide React** | Icon system |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker Compose** | Multi-container orchestration (PostgreSQL + Backend + Frontend) |
| **pgvector** | Vector similarity search for RAG embeddings |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 14)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────────┐  │
│  │Dashboard │ │Analytics │ │ Upload   │ │ AI Advisor Chat   │  │
│  │Budgets   │ │Forecast  │ │ Documents│ │ Philosophy Compare│  │
│  │Goals     │ │Anomalies │ │ Receipts │ │ Guru Personas     │  │
│  │Settings  │ │Simulator │ │ CSV/PDF  │ │ RAG Knowledge     │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API (fetch)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   API Layer (v1)                          │   │
│  │  /auth  /transactions  /documents  /analytics  /advisor  │   │
│  │  /budgets  /goals  /subscriptions  /reports              │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         ▼                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────────────────┐  │
│  │ Services    │ │ ML Engine   │ │ AI Engine                │  │
│  │ Auth        │ │ Categorizer │ │ LangGraph Agent          │  │
│  │ Ingestion   │ │ Forecaster  │ │ RAG Engine               │  │
│  │ Analytics   │ │ Anomaly Det.│ │ Guru Personas            │  │
│  │ Reports     │ │ Sub Tracker │ │ Red Team / Eval          │  │
│  └─────────────┘ └─────────────┘ └──────────────────────────┘  │
│                         ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Data Layer (SQLAlchemy + Repositories)         │   │
│  │  Users · Transactions · Categories · Documents · Budgets │   │
│  │  Goals · Subscriptions · Anomalies · Chat · Audit Logs   │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
                  ┌─────────────────────┐
                  │  PostgreSQL 16      │
                  │  + pgvector         │
                  └─────────────────────┘
```

---

## Getting Started

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **Docker & Docker Compose** (for PostgreSQL)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/devkalon/FinSight-AI.git
cd FinSight-AI
```

### 2. Start the Database

```bash
docker compose up -d db
```

This launches a PostgreSQL 16 container with pgvector on port `5432`.

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
DATABASE_URL=postgresql+asyncpg://finsight_user:finsight_secure_pass_2026@localhost:5432/finsight_db
SECRET_KEY=your-secure-random-key-here

# Optional — Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback/google

# Optional — LLM API Keys (for AI Advisor)
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
```

### 4. Install & Run the Backend

```bash
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 5. Install & Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`.

### Docker Compose (Full Stack)

To run everything in containers:

```bash
docker compose up --build
```

This starts PostgreSQL, the FastAPI backend, and the Next.js frontend — all wired together automatically.

---

## API Reference

All endpoints are prefixed with `/api/v1`.

| Module | Endpoints | Description |
|---|---|---|
| **Auth** | `POST /auth/register`, `POST /auth/login`, `POST /auth/google`, `POST /auth/logout`, `GET /auth/me` | User registration, login, Google OAuth, profile |
| **Transactions** | `GET /transactions/`, `POST /transactions/`, `PUT /transactions/{id}`, `DELETE /transactions/{id}` | CRUD operations on financial transactions |
| **Documents** | `POST /documents/upload/receipt`, `POST /documents/upload/bank-statement`, `POST /documents/{id}/confirm` | Document upload, OCR processing, transaction extraction |
| **Analytics** | `GET /analytics/dashboard`, `GET /analytics/forecast`, `GET /analytics/anomalies`, `POST /analytics/simulation` | Dashboard data, forecasting, anomaly detection, what-if simulation |
| **Health Score** | `GET /analytics/health-score`, `GET /analytics/health-score/history` | Financial health scoring with historical tracking |
| **Budgets** | `GET /budgets/`, `POST /budgets/`, `DELETE /budgets/{id}` | Budget creation and tracking |
| **Goals** | `GET /goals/`, `POST /goals/`, `POST /goals/{id}/contribute`, `DELETE /goals/{id}` | Financial goal management with contributions |
| **Subscriptions** | `GET /subscriptions/`, `POST /subscriptions/scan`, `POST /subscriptions/{id}/confirm` | Recurring payment detection and management |
| **Advisor** | `POST /advisor/chat`, `POST /advisor/compare` | AI financial advisor chat and philosophy comparison |
| **Reports** | `GET /reports/export/pdf` | Monthly financial report generation (PDF) |

Full interactive API documentation is available at `/docs` (Swagger UI) when the backend is running.

---

## Testing

The project includes **27 test modules** with comprehensive coverage across all layers:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test module
pytest tests/test_financial_advisor_agent.py -v
```

### Test Coverage

| Area | Test File | What It Tests |
|---|---|---|
| Auth & Security | `test_security_and_auth.py` | JWT, password hashing, OAuth, token revocation |
| Database Models | `test_database_models.py` | All 14 SQLAlchemy models and relationships |
| Transactions | `test_transactions.py` | CRUD, filtering, category assignment |
| Document Ingestion | `test_document_ingestion.py` | PDF parsing, OCR, CSV import |
| Indian Formats | `test_indian_financial_ingestion.py` | ₹ parsing, UPI, HDFC/ICICI/SBI adapters |
| Categorization | `test_expense_categorization_engine.py` | ML categorizer, merchant learning |
| Forecasting | `test_expense_forecasting.py` | Time-series prediction, seasonal adjustments |
| Anomaly Detection | `test_financial_anomaly_detector.py` | Six detection strategies |
| Health Score | `test_financial_health_score.py` | Composite scoring, sub-scores |
| AI Advisor | `test_financial_advisor_agent.py` | Agent tools, reasoning, persona responses |
| RAG Engine | `test_financial_knowledge_rag.py` | Document retrieval, embedding, context building |
| Budgets & Goals | `test_budgets_and_goals.py` | Budget tracking, goal contributions |
| Subscriptions | `test_recurring_subscriptions.py` | Recurring payment detection |
| What-If Simulator | `test_whatif_simulator.py` | Scenario modeling |
| Reports | `test_monthly_financial_report.py` | PDF generation, chart data |
| AI Safety | `test_ai_grounding_and_safety.py` | Hallucination detection, grounding validation |
| E2E Workflow | `test_e2e_complete_workflow.py` | Full user journey from signup to insights |
| Performance | `test_performance_benchmark.py` | Response time benchmarks |

---

## Project Structure

```
FinSight-AI/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # FastAPI route handlers
│   │   ├── core/                 # Config, database, security
│   │   ├── models/               # SQLAlchemy ORM models (14 models)
│   │   ├── repositories/         # Data access layer
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── ai/               # LangGraph agent, RAG, guru personas
│   │   │   ├── ml/               # Categorizer, forecaster, anomaly detector
│   │   │   └── ingestion/        # PDF, OCR, CSV parsers + bank adapters
│   │   └── main.py               # FastAPI application entry point
│   ├── alembic/                  # Database migrations
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js App Router pages (14 pages)
│   │   ├── components/           # Shared UI components
│   │   ├── context/              # React context (Auth)
│   │   └── lib/                  # API client, utilities
│   └── Dockerfile
├── tests/                        # 27 test modules
├── docker-compose.yml            # Full-stack orchestration
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment variable template
```

---

## License

This project is for educational and personal use.

---

## Credits

Built by **Kartik** ([@devkalon](https://github.com/devkalon))
Built by **Kalavathi** ([@MadeByKala](https://github.com/MadebyKala))

---

<p align="center">
  <img src="logo.png" alt="FinSight AI" width="200" />
  <br />
  <sub>Insights Today. Wealth Tomorrow.</sub>
</p>
