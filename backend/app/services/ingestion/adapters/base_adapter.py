from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd

class BankStatementAdapter(ABC):
    """
    Base Adapter interface for Indian bank statements and UPI exports.
    Allows bank statement formats to be added as modular plugins without modifying core ingestion logic.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def bank_code(self) -> str:
        pass

    @abstractmethod
    def matches_format(self, columns: List[str], sample_text: str = "") -> bool:
        """
        Determines whether this adapter matches the provided statement column headers or text layout.
        """
        pass

    @abstractmethod
    def parse_dataframe(self, df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parses a normalized DataFrame into standardized transaction candidate dictionaries.
        Returns:
            (transactions_list, statement_summary)
        """
        pass

    @staticmethod
    def find_matching_column(columns: List[str], candidates: List[str]) -> Optional[str]:
        """
        Robust column matching that prioritizes exact matches and avoids short substring collisions (e.g. 'cr' vs 'description').
        """
        # Pass 1: Exact match
        for cand in candidates:
            for c in columns:
                if cand.lower() == c.lower().strip():
                    return c
        # Pass 2: Substring match (only for keywords > 2 chars)
        for cand in candidates:
            if len(cand) <= 2:
                continue
            for c in columns:
                if cand.lower() in c.lower():
                    return c
        return None
