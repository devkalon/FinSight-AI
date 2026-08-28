import uuid
from typing import List, Dict, Any, Tuple
import pandas as pd
from backend.app.services.ingestion.adapters.base_adapter import BankStatementAdapter
from backend.app.services.ingestion.indian_normalization import indian_normalizer

class UPIExportAdapter(BankStatementAdapter):
    """
    Adapter for UPI Statement Exports (PhonePe, Google Pay, Paytm, BHIM).
    Handles UPI reference numbers (RRN), VPA counterparties, and payment statuses.
    """

    @property
    def name(self) -> str:
        return "UPI Transaction Export Adapter (PhonePe / GPay / Paytm)"

    @property
    def bank_code(self) -> str:
        return "upi_export"

    def matches_format(self, columns: List[str], sample_text: str = "") -> bool:
        cols_lower = [c.lower().strip() for c in columns]
        # Check PhonePe / GPay headers: 'transaction id', 'utr', 'paid to', 'received from', 'type', 'vpa'
        has_upi_cols = any(k in c for c in cols_lower for k in ["utr", "transaction id", "paid to", "payment type", "vpa", "to/from"])
        has_upi_text = any(k in sample_text.lower() for k in ["phonepe", "google pay", "gpay", "paytm payments", "bhim upi"])
        return has_upi_cols or has_upi_text

    def parse_dataframe(self, df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        results = []
        df.columns = [str(c).strip().lower() for c in df.columns]

        date_col = next((c for c in df.columns if any(k in c for k in ["date", "timestamp", "time", "date & time"])), None)
        desc_col = next((c for c in df.columns if any(k in c for k in ["paid to", "received from", "to/from", "details", "description", "recipient", "merchant"])), None)
        ref_col = next((c for c in df.columns if any(k in c for k in ["utr", "transaction id", "txn id", "rrn", "ref"])), None)
        amount_col = next((c for c in df.columns if any(k in c for k in ["amount", "txn amount", "total"])), None)
        type_col = next((c for c in df.columns if any(k in c for k in ["type", "payment type", "dr/cr", "credit/debit"])), None)
        status_col = next((c for c in df.columns if any(k in c for k in ["status", "txn status", "payment status"])), None)

        for idx, row in df.iterrows():
            # Skip failed transactions if status column is present
            if status_col and pd.notna(row[status_col]):
                status_str = str(row[status_col]).strip().lower()
                if any(f in status_str for f in ["failed", "declined", "cancelled", "reversed"]):
                    continue

            raw_date = row[date_col] if date_col and pd.notna(row[date_col]) else None
            tx_date = indian_normalizer.parse_indian_date(raw_date)

            raw_desc = str(row[desc_col]).strip() if desc_col and pd.notna(row[desc_col]) else "UPI Transfer"
            ref_no = str(row[ref_col]).strip() if ref_col and pd.notna(row[ref_col]) else None

            amount = indian_normalizer.parse_indian_amount(row[amount_col]) if amount_col and pd.notna(row[amount_col]) else 0.0

            tx_type = "debit"
            if type_col and pd.notna(row[type_col]):
                t_str = str(row[type_col]).lower()
                if any(c in t_str for c in ["credit", "cr", "received", "deposit", "cashback", "refund"]):
                    tx_type = "credit"
                else:
                    tx_type = "debit"
            elif any(k in raw_desc.lower() for k in ["received from", "cashback", "refund", "salary"]):
                tx_type = "credit"

            if amount > 0:
                merchant, subcat, utr = indian_normalizer.extract_indian_merchant(raw_desc)
                category, default_subcat = indian_normalizer.categorize_indian_transaction(merchant or raw_desc)
                final_subcat = subcat or default_subcat

                final_ref = utr or (ref_no if ref_no and ref_no not in ["-", "nan", "0"] else None)
                fingerprint = indian_normalizer.generate_transaction_fingerprint(
                    tx_date=tx_date,
                    amount=amount,
                    merchant_name=merchant,
                    tx_type=tx_type,
                    utr_ref=final_ref
                )

                results.append({
                    "id": str(uuid.uuid4()),
                    "transaction_date": tx_date.isoformat(),
                    "description": raw_desc,
                    "merchant_name": merchant,
                    "amount": amount,
                    "currency": "INR",
                    "transaction_type": tx_type,
                    "category_suggestion": category,
                    "subcategory": final_subcat,
                    "payment_method": "UPI",
                    "source": "upi_export",
                    "confidence_score": 0.97,
                    "fingerprint": fingerprint,
                    "reference_number": final_ref,
                    "is_confirmed": False
                })

        summary = indian_normalizer.validate_statement_integrity(None, None, results)
        summary["bank_adapter"] = self.name
        summary["bank_code"] = self.bank_code

        return results, summary
