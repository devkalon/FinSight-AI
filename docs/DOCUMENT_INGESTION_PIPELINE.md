# FinSight AI — Advanced Financial Document Ingestion Pipeline

## Overview
The **Financial Document Ingestion Pipeline** provides an automated, multi-source ingestion framework for FinSight AI. It supports payment screenshots, physical and digital receipts, PDF bank statements, and CSV exports with local PII scrubbing, image preprocessing, multi-tier OCR provider abstraction, granular confidence scoring, and an interactive candidate verification flow before committing to the primary financial ledger.

---

## Ingestion Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Upload Layer                                   │
│  - Payment Screenshots & Receipts (JPG, PNG, WebP)                          │
│  - Bank Statement PDFs & CSV Exports                                        │
│  - MIME type validation & 15MB file size limit                              │
│  - Filename sanitization & secure non-executable storage                    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Preprocessing Layer                               │
│  - EXIF orientation auto-correction                                         │
│  - Grayscale conversion (LANCZOS upscaling / Bilinear downscaling)          │
│  - Adaptive contrast & sharpness enhancement (Median denoising filter)      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Multi-Tier OCR / Parsing Engine                           │
│  - OCR Provider Abstraction: `OCRProviderInterface`                         │
│  - Primary: `TesseractOCRProvider` (Local Pytesseract Engine)               │
│  - Secondary: `VisionAIProvider` (Multimodal AI Provider)                   │
│  - Fallback: `PatternHeuristicOCRProvider` (Structural Pattern Analyzer)    │
│  - PDF Table Parser (`pdfplumber` / `pypdf`) & CSV Parser (`pandas`)        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                Text Normalization & Entity Extraction                       │
│  - Local PII Scrubbing (PAN, Aadhaar, Credit Card numbers redacted)         │
│  - Merchant recognition & currency detection (INR, USD, EUR, GBP)           │
│  - Multi-format date parsing & subcategory classification                   │
│  - Composite Confidence Scoring (Amount 35%, Merchant 25%, Date 20%, OCR 20%)│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Candidate Generation & Review Flow                       │
│  - Returns structured `CandidateTransaction` list marked unconfirmed        │
│  - Next.js Interactive Verification Drawer with inline field edits          │
│  - User Confirmation Endpoint: `POST /api/v1/documents/{doc_id}/confirm`    │
│  - Atomic write into primary `transactions` ledger (`Numeric(14, 2)`)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## OCR Provider Interface & Abstraction

The OCR subsystem adheres to a strict interface decoupling extraction algorithms from business and service logic:

```python
class OCRProviderInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def extract_text(self, image: Image.Image, context: Optional[Dict[str, Any]] = None) -> Tuple[str, float, str]:
        pass
```

### Provider Fallback Hierarchy:
1. **Primary Provider** (`Tesseract-OCR`): Executes local OCR against preprocessed image buffers.
2. **Multimodal Vision Provider** (`Vision-AI-Multimodal`): Optional cloud vision provider using secure environment keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`).
3. **Deterministic Fallback Provider** (`Heuristic-Pattern-OCR`): Resilient structural layout detector and pattern recognizer ensuring 100% uptime even in offline or missing-binary environments.

---

## REST Endpoints

### 1. Ingest Payment Screenshot or Receipt
`POST /api/v1/documents/upload/receipt`
- **Payload**: `multipart/form-data` with `file` (PNG, JPG, WebP)
- **Response**: `OCRUploadResponse` with structured `candidates` and composite `confidence_score`.

### 2. Ingest Bank Statement (PDF / CSV)
`POST /api/v1/documents/upload/bank-statement`
- **Payload**: `multipart/form-data` with `file` (PDF, CSV)
- **Response**: `BankStatementParseResponse` with tabular parsed transactions, account summary, and candidates.

### 3. Confirm & Commit Candidate Transactions
`POST /api/v1/documents/{doc_id}/confirm`
- **Payload**:
```json
{
  "transactions": [
    {
      "description": "Starbucks Coffee & Snacks",
      "merchant_name": "Starbucks",
      "amount": 490.0,
      "currency": "INR",
      "transaction_type": "debit",
      "transaction_date": "2026-08-28",
      "category_suggestion": "Food & Dining",
      "subcategory": "Coffee & Bakery",
      "payment_method": "UPI",
      "source": "ocr_receipt",
      "confidence_score": 0.95
    }
  ]
}
```
- **Response**:
```json
{
  "document_id": "...",
  "committed_count": 1,
  "transaction_ids": ["..."],
  "message": "Successfully committed 1 transactions to your financial ledger."
}
```

### 4. Document Management
- `GET /api/v1/documents/`: List all ingested documents for authenticated user.
- `GET /api/v1/documents/{doc_id}`: Retrieve single document with parsing metadata.
- `DELETE /api/v1/documents/{doc_id}`: Securely delete document and its storage reference.
