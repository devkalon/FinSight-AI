import re
import hashlib
from datetime import datetime, date
from typing import Dict, Any, Tuple, Optional, List
from decimal import Decimal

class IndianFinancialNormalizer:
    """
    Normalization Layer for Indian Financial Data.
    Standardizes dates, amounts with Lakhs/Crores numbering, UPI references,
    merchant extraction from Indian bank narrations, and transaction duplicate fingerprinting.
    """

    MONTH_MAP = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }

    KNOWN_INDIAN_MERCHANTS = [
        # Tech & Payroll
        "tech corp", "tcs", "infosys", "wipro", "hcl", "accenture", "cognizant",
        # Food & Delivery
        "swiggy", "zomato", "blinkit", "zepto", "bigbasket", "bbdaily", "dunzo", "eatclub",
        # E-Commerce & Retail
        "amazon", "flipkart", "myntra", "meesho", "ajio", "nykaa", "tata cliq", "croma", "reliance digital",
        "dmart", "reliance fresh", "spencers", "more retail", "nature basket",
        # Cab & Travel
        "uber", "ola", "rapido", "irctc", "makemytrip", "goibibo", "easemytrip", "yatra", "redbus", "indigo", "air india",
        # Fuel & Auto
        "shell", "hpcl", "bpcl", "indane", "ioc", "iocl", "petrol", "fuel", "fastag",
        # Telecom & Utilities
        "airtel", "jio", "vi", "vodafone", "idea", "bescom", "tneb", "mseb", "mahadiscom", "bses", "tatasky", "tata play",
        # Subscriptions & Entertainment
        "netflix", "spotify", "hotstar", "disney", "prime video", "bookmyshow", "pvr", "inox", "youtube", "apple",
        # Healthcare & Fitness
        "cult fit", "cultfit", "cult.fit", "apollo", "1mg", "tata 1mg", "pharmeasy", "netmeds", "medplus",
        # Quick Service Restaurants
        "starbucks", "mcdonalds", "dominos", "subway", "kfc", "burger king", "pizza hut", "chai point", "chaayos",
        # Investments & Banking
        "zerodha", "groww", "upstox", "kuvera", "indmoney", "hdfc mutual", "sbi mutual", "icici pru", "uti mutual", "axis mutual"
    ]

    @classmethod
    def parse_indian_amount(cls, val: Any) -> float:
        """
        Parses Indian and standard numeric strings into float.
        Handles Lakhs/Crores notation (e.g. 1,50,000.00 or 1,23,456.78), currency symbols (₹, Rs., INR),
        trailing CR/DR indicators, and negative signs.
        """
        if val is None:
            return 0.0
        if isinstance(val, (int, float)):
            return float(abs(val))

        s = str(val).strip()
        if not s or s.lower() in ["nan", "null", "none", "-"]:
            return 0.0

        # Strip currency words & symbols without touching the decimal point
        clean = re.sub(r"(?i)\b(inr|rs|cr|dr|/-)\b|[₹,\/]", "", s).strip()

        # Extract number with decimal point preserved
        match = re.search(r"[-+]?\d+(?:\.\d+)?", clean)
        if match:
            try:
                num = float(match.group(0))
                return abs(num)
            except ValueError:
                return 0.0
        return 0.0

    @classmethod
    def parse_indian_date(cls, val: Any) -> date:
        """
        Normalizes multi-format Indian date styles to a standard datetime.date:
        - DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
        - DD/MM/YY, DD-MM-YY
        - DD-Mon-YYYY (e.g., 15-Aug-2026, 01-JAN-26)
        - YYYY-MM-DD
        """
        if not val:
            return date.today()
        if isinstance(val, date):
            return val
        if isinstance(val, datetime):
            return val.date()

        s = str(val).strip()
        if not s or s.lower() in ["nan", "null", "none", "-"]:
            return date.today()

        # If date string has timestamp: "2026-08-01 10:15:00" -> split by space
        s_date_part = s.split()[0].strip()
        s_clean = re.sub(r"[\/\.]", "-", s_date_part).strip()

        # Check for textual month: e.g., "15-Aug-2026" or "15-Aug-26"
        text_month_match = re.match(r"^(\d{1,2})[- ]([A-Za-z]{3})[- ](\d{2,4})$", s_clean)
        if text_month_match:
            day = int(text_month_match.group(1))
            mon_str = text_month_match.group(2).lower()
            year = int(text_month_match.group(3))
            if year < 100:
                year += 2000
            month = cls.MONTH_MAP.get(mon_str, 1)
            try:
                return date(year, month, day)
            except ValueError:
                return date.today()

        # Check standard numeric patterns
        formats = [
            "%d-%m-%Y", "%Y-%m-%d", "%d-%m-%y", "%m-%d-%Y",
            "%d %b %Y", "%d %B %Y", "%Y/%m/%d"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(s_clean, fmt).date()
            except Exception:
                continue

        return date.today()

    @classmethod
    def extract_indian_merchant(cls, narration: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Extracts merchant name, subcategory, and reference UTR from Indian banking narrations.
        Supports UPI, POS, NEFT, RTGS, IMPS, ACH, and BillPay patterns.
        Returns: (merchant_name, subcategory, utr_ref)
        """
        if not narration:
            return "Bank Transaction", None, None

        raw = narration.strip()
        text_lower = raw.lower()
        utr_ref = None

        # 1. Extract UTR / Reference number if present
        utr_match = re.search(r"\b(\d{12})\b", raw) # Standard 12-digit Indian UPI RRN / UTR
        if utr_match:
            utr_ref = utr_match.group(1)

        # 2. Check known merchants in full narration first
        for km in cls.KNOWN_INDIAN_MERCHANTS:
            if km in text_lower:
                category, subcat = cls.categorize_indian_transaction(km)
                return km.title(), subcat, utr_ref

        # 3. UPI Narration Extraction (e.g., UPI/123456789012/Swiggy/swiggy@icici or UPI-SWIGGY-swiggy@icici)
        if "upi" in text_lower:
            parts = re.split(r"[/_-]", raw)
            for part in parts:
                p_clean = part.strip()
                if not p_clean or p_clean.isdigit() or len(p_clean) < 3 or p_clean.lower() in ["upi", "cr", "dr", "paytm", "gpay", "phonepe"]:
                    continue
                if "@" in p_clean:
                    vpa_name = p_clean.split("@")[0]
                    if len(vpa_name) > 2 and not vpa_name.isdigit():
                        return vpa_name.title(), "UPI Transfer", utr_ref
                if re.match(r"^[A-Za-z\s]+$", p_clean) and len(p_clean) > 3:
                    return p_clean.title(), "UPI Transfer", utr_ref

        # 4. POS / Card Narration (e.g. POS 401234XXXXXX1234 STARBUCKS BANGALORE IN)
        pos_match = re.search(r"(?:pos|ecom pur|card purchase)[ -]+(?:\d+x+\d+[ -]+)?([A-Za-z0-9\s]+?)(?:bangalore|mumbai|delhi|hyderabad|chennai|in\b|\d{6}|$)", raw, re.IGNORECASE)
        if pos_match:
            candidate = pos_match.group(1).strip()
            if len(candidate) > 2:
                for km in cls.KNOWN_INDIAN_MERCHANTS:
                    if km in candidate.lower():
                        _, subcat = cls.categorize_indian_transaction(km)
                        return km.title(), subcat, utr_ref
                return candidate.title(), "Card Purchase", utr_ref

        # 5. NEFT / RTGS / IMPS Narration (e.g. NEFT CR-N12345678-TECH CORP-SALARY)
        transfer_match = re.search(r"(?:neft|rtgs|imps)[ -_/]+(?:cr|dr)?[-_/]?[A-Za-z0-9]+[ -_/]+([A-Za-z0-9\s]+?)(?:[ -_/]|$)", raw, re.IGNORECASE)
        if transfer_match:
            cand = transfer_match.group(1).strip()
            if len(cand) > 2:
                return cand.title(), "Bank Transfer", utr_ref

        # 6. ACH / NACH / SIP Narration (e.g. ACH D- HDFC MUTUAL FUND SIP)
        if any(k in text_lower for k in ["ach", "nach", "ecs", "sip"]):
            return "Auto-Debit / SIP", "Investments", utr_ref

        # Default fallback to cleaned first words
        clean_first = re.sub(r"[^A-Za-z0-9\s]", " ", raw).strip()
        words = clean_first.split()
        if words:
            return " ".join(words[:3]).title(), "General", utr_ref

        return "Bank Counterparty", "General", utr_ref

    @classmethod
    def categorize_indian_transaction(cls, merchant_or_narration: str) -> Tuple[str, str]:
        """
        Maps Indian merchants and keywords to standard Category and Subcategory.
        """
        text = merchant_or_narration.lower()
        if any(k in text for k in ["swiggy", "zomato", "eatclub", "restaurant", "dining", "cafe", "biryani", "chai"]):
            return "Food & Dining", "Food Delivery & Restaurants"
        if any(k in text for k in ["blinkit", "zepto", "bigbasket", "bbdaily", "dmart", "reliance fresh", "supermarket", "grocery"]):
            return "Groceries", "Quick Commerce & Supermarkets"
        if any(k in text for k in ["uber", "ola", "rapido", "metro", "fuel", "petrol", "shell", "hpcl", "bpcl", "fastag", "toll"]):
            return "Transportation", "Rides, Fuel & Toll"
        if any(k in text for k in ["amazon", "flipkart", "myntra", "meesho", "ajio", "nykaa", "croma", "retail", "shopping"]):
            return "Shopping", "Online Retail & Electronics"
        if any(k in text for k in ["airtel", "jio", "vi", "bescom", "tneb", "mseb", "electricity", "broadband", "tatasky", "gas", "indane"]):
            return "Utilities & Bills", "Electricity, Mobile & Gas"
        if any(k in text for k in ["netflix", "spotify", "hotstar", "prime video", "bookmyshow", "pvr", "inox", "youtube"]):
            return "Entertainment", "Streaming & Movies"
        if any(k in text for k in ["zerodha", "groww", "upstox", "mutual fund", "sip", "kuvera", "indmoney"]):
            return "Investment & Savings", "Mutual Funds & Stocks"
        if any(k in text for k in ["cult", "apollo", "1mg", "pharmeasy", "hospital", "doctor", "pharmacy"]):
            return "Healthcare & Fitness", "Gym & Medicine"
        if any(k in text for k in ["salary", "payroll", "stipend", "bonus", "dividend", "tech corp", "tcs", "infosys", "wipro"]):
            return "Income", "Salary & Compensation"
        return "General Expense", "Miscellaneous"

    @classmethod
    def generate_transaction_fingerprint(
        cls,
        tx_date: date,
        amount: float,
        merchant_name: Optional[str],
        tx_type: str,
        utr_ref: Optional[str] = None
    ) -> str:
        amt_str = f"{round(amount, 2):.2f}"
        m_str = (merchant_name or "").strip().lower()
        if utr_ref and len(utr_ref.strip()) >= 6:
            raw_key = f"UTR:{utr_ref.strip()}:{amt_str}"
        else:
            raw_key = f"{tx_date.isoformat()}:{amt_str}:{m_str}:{tx_type.lower()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def validate_statement_integrity(
        cls,
        opening_balance: Optional[float],
        closing_balance: Optional[float],
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        total_debits = sum(t.get("amount", 0.0) for t in transactions if t.get("transaction_type") == "debit")
        total_credits = sum(t.get("amount", 0.0) for t in transactions if t.get("transaction_type") == "credit")

        is_balanced = True
        discrepancy = 0.0

        if opening_balance is not None and closing_balance is not None:
            expected_closing = round(opening_balance + total_credits - total_debits, 2)
            actual_closing = round(closing_balance, 2)
            discrepancy = round(abs(expected_closing - actual_closing), 2)
            is_balanced = discrepancy <= 0.05

        return {
            "total_transactions": len(transactions),
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "opening_balance": opening_balance,
            "closing_balance": closing_balance,
            "is_balanced": is_balanced,
            "balance_discrepancy": discrepancy
        }

indian_normalizer = IndianFinancialNormalizer()
