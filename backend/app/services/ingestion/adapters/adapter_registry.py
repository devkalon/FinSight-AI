from typing import List, Dict, Optional, Tuple
import pandas as pd
from backend.app.services.ingestion.adapters.base_adapter import BankStatementAdapter
from backend.app.services.ingestion.adapters.hdfc_adapter import HDFCBankAdapter
from backend.app.services.ingestion.adapters.sbi_adapter import SBIBankAdapter
from backend.app.services.ingestion.adapters.icici_adapter import ICICIBankAdapter
from backend.app.services.ingestion.adapters.upi_adapter import UPIExportAdapter
from backend.app.services.ingestion.adapters.generic_adapter import GenericIndianBankAdapter

class BankAdapterRegistry:
    """
    Registry for statement adapters. Auto-detects matching bank formats
    and provides extension points for new bank formats without altering core ingestion logic.
    """

    def __init__(self):
        self.adapters: List[BankStatementAdapter] = [
            HDFCBankAdapter(),
            SBIBankAdapter(),
            ICICIBankAdapter(),
            UPIExportAdapter(),
            GenericIndianBankAdapter()
        ]
        self._adapter_map: Dict[str, BankStatementAdapter] = {
            a.bank_code: a for a in self.adapters
        }

    def register_adapter(self, adapter: BankStatementAdapter, prepend: bool = True):
        """Register a new bank adapter plugin."""
        if prepend:
            self.adapters.insert(0, adapter)
        else:
            self.adapters.append(adapter)
        self._adapter_map[adapter.bank_code] = adapter

    def get_adapter_by_code(self, bank_code: str) -> Optional[BankStatementAdapter]:
        return self._adapter_map.get(bank_code)

    def detect_adapter(self, columns: List[str], sample_text: str = "") -> BankStatementAdapter:
        """
        Inspects column headers and sample text to find the best matching bank adapter.
        Falls back to GenericIndianBankAdapter if no specific bank pattern matches.
        """
        for adapter in self.adapters:
            if adapter.bank_code != "generic_in" and adapter.matches_format(columns, sample_text):
                return adapter
        return self._adapter_map.get("generic_in", self.adapters[-1])

adapter_registry = BankAdapterRegistry()
