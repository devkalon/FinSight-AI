# FinSight AI — Indian Financial Data Ingestion & Normalization Layer

## Overview
FinSight AI includes an extensible normalization layer specifically designed for Indian financial instruments and banking statements. It provides multi-bank adapter support (HDFC, SBI, ICICI, Axis), UPI transaction export parsing (PhonePe, Google Pay, Paytm, BHIM), Indian date & amount normalization (Lakhs/Crores numbering), advanced Indian narration merchant extraction, duplicate transaction fingerprinting, and mathematical statement balance validation.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             Multi-Format Input                              │
│   - Bank Statement CSVs (HDFC, SBI, ICICI, Axis, Kotak, Generic)            │
│   - Bank Statement PDFs (Tabular & text extract)                            │
│   - UPI Transaction Exports (PhonePe, GPay, Paytm CSVs)                     │
│   - Receipt PDFs & Invoices (Swiggy, Zomato, Amazon, Bescom, IRCTC)         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Bank Adapter Registry                             │
│   - `HDFCBankAdapter`                                                       │
│   - `SBIBankAdapter`                                                        │
│   - `ICICIBankAdapter`                                                      │
│   - `UPIExportAdapter`                                                      │
│   - `GenericIndianBankAdapter` (Universal fallback)                         │
│   - Dynamic extension hook: `adapter_registry.register_adapter(custom)`     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Indian Financial Normalization Engine                    │
│   - Amount: Lakhs/Crores parsing (`1,50,000.00`, `₹ 12,34,567.89`)          │
│   - Dates: Multi-format Indian dates (`DD/MM/YYYY`, `DD-Mon-YYYY`, `DD/MM/YY`)│
│   - Currency: Standardization to ISO `INR` (₹)                              │
│   - Narrations: Regex extraction for UPI VPA/RRN, POS, NEFT, ACH, BillPay   │
│   - Duplicates: SHA-256 fingerprinting `(Date, Amount, Merchant, Type, UTR)`│
│   - Integrity: Equation `Opening Bal + Credits - Debits == Closing Bal`     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Candidate Review & Confirmation                        │
│   - Returns structured `CandidateTransaction` list marked with duplicates   │
│   - Interactive Next.js Verification Interface                              │
│   - Balance Integrity Check Display                                         │
│   - Commit endpoint: `POST /api/v1/documents/{doc_id}/confirm`              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Supported Indian Terminology & Patterns

1. **UPI Patterns**:
   - `UPI-SWIGGY-swiggy@icici-902183129012` &rarr; Merchant: `Swiggy`, Mode: `UPI`, UTR: `902183129012`
   - `UPI/DR/123456789012/ZOMATO/zomato@axis` &rarr; Merchant: `Zomato`, Mode: `UPI`, UTR: `123456789012`
2. **POS / Card Swipes**:
   - `POS 401234XXXXXX1234 STARBUCKS BANGALORE IN` &rarr; Merchant: `Starbucks`, Mode: `Card Purchase`
   - `ECOM PUR/AMAZON PAY INDIA/MUMBAI` &rarr; Merchant: `Amazon`, Mode: `Online Retail`
3. **NEFT / RTGS / IMPS**:
   - `NEFT CR-N12345678-TECH CORP-SALARY AUGUST 2026` &rarr; Merchant: `Tech Corp`, Category: `Income`
4. **ACH / NACH / SIP**:
   - `ACH D- HDFC MUTUAL FUND SIP-901283` &rarr; Merchant: `Hdfc Mutual`, Category: `Investment & Savings`
5. **Utility Bills & Travel**:
   - `BILLPAY-BESCOM-BLR-01293` &rarr; Merchant: `Bescom`, Category: `Utilities & Bills`
   - `IRCTC WEB TICKETING NEW DELHI` &rarr; Merchant: `IRCTC`, Category: `Transportation`

---

## Adding Custom Bank Adapters

New bank formats can be registered with zero modifications to core services:

```python
from backend.app.services.ingestion.adapters.base_adapter import BankStatementAdapter
from backend.app.services.ingestion.adapters.adapter_registry import adapter_registry

class KotakBankAdapter(BankStatementAdapter):
    @property
    def name(self) -> str:
        return "Kotak Mahindra Bank Statement Adapter"

    @property
    def bank_code(self) -> str:
        return "kotak"

    def matches_format(self, columns, sample_text="") -> bool:
        return any("kotak" in c.lower() for c in columns) or "kotak" in sample_text.lower()

    def parse_dataframe(self, df):
        # Implementation using indian_normalizer
        ...
        return candidates, summary

# Register adapter dynamically
adapter_registry.register_adapter(KotakBankAdapter())
```
