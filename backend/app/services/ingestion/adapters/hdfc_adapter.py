import uuid
from typing import List, Dict, Any, Tuple
import pandas as pd
from backend.app.services.ingestion.adapters.base_adapter import BankStatementAdapter
from backend.app.services.ingestion.indian_normalization import indian_normalizer

class HDFCBankAdapter(BankStatementAdapter):
    """
    Adapter for HDFC Bank Statement exports (CSV & Tabular).
    """

    @property
    def name(self) -> str:
        return "HDFC Bank Statement Adapter"

    @property
    def bank_code(self) -> str:
        return "hdfc"

    def matches_format(self, columns: List[str], sample_text: str = "") -> bool:
        cols_lower = [c.lower().strip() for c in columns]
        has_narration = any("narration" in c for c in cols_lower)
        has_chq_ref = any("chq" in c or "ref" in c for c in cols_lower)
        has_withdrawal = any("withdrawal" in c or "debit" in c for c in cols_lower)
        has_hdfc_text = "hdfc" in sample_text.lower()
        return (has_narration and (has_chq_ref or has_withdrawal)) or has_hdfc_text

    def parse_dataframe(self, df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        results = []
        df.columns = [str(c).strip().lower() for c in df.columns]

        date_col = self.find_matching_column(df.columns, ["date", "txn date", "value dt", "transaction date"])
        desc_col = self.find_matching_column(df.columns, ["narration", "particulars", "description", "details"])
        ref_col = self.find_matching_column(df.columns, ["chq./ref.no.", "chq", "ref", "ref no", "utr"])
        debit_col = self.find_matching_column(df.columns, ["withdrawal amt.", "withdrawal", "debit", "dr"])
        credit_col = self.find_matching_column(df.columns, ["deposit amt.", "deposit", "credit", "cr"])
        bal_col = self.find_matching_column(df.columns, ["closing balance", "balance", "bal"])

        opening_balance = None
        closing_balance = None

        for idx, row in df.iterrows():
            raw_date = row[date_col] if date_col and pd.notna(row[date_col]) else None
            tx_date = indian_normalizer.parse_indian_date(raw_date)

            raw_desc = str(row[desc_col]).strip() if desc_col and pd.notna(row[desc_col]) else "HDFC Bank Transaction"
            ref_no = str(row[ref_col]).strip() if ref_col and pd.notna(row[ref_col]) else None

            debit_val = indian_normalizer.parse_indian_amount(row[debit_col]) if debit_col and pd.notna(row[debit_col]) else 0.0
            credit_val = indian_normalizer.parse_indian_amount(row[credit_col]) if credit_col and pd.notna(row[credit_col]) else 0.0

            amount = 0.0
            tx_type = "debit"
            if debit_val > 0:
                amount = debit_val
                tx_type = "debit"
            elif credit_val > 0:
                amount = credit_val
                tx_type = "credit"

            if bal_col and pd.notna(row[bal_col]):
                curr_bal = indian_normalizer.parse_indian_amount(row[bal_col])
                if opening_balance is None:
                    opening_balance = curr_bal + debit_val - credit_val
                closing_balance = curr_bal

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

                payment_method = "UPI" if "upi" in raw_desc.lower() else "Net Banking"

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
                    "payment_method": payment_method,
                    "source": "bank_statement_csv",
                    "confidence_score": 0.96,
                    "fingerprint": fingerprint,
                    "reference_number": final_ref,
                    "is_confirmed": False
                })

        summary = indian_normalizer.validate_statement_integrity(opening_balance, closing_balance, results)
        summary["bank_adapter"] = self.name
        summary["bank_code"] = self.bank_code

        return results, summary
