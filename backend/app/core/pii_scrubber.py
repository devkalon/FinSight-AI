import re
from typing import Tuple, Dict

class PIIScrubber:
    """
    Local privacy scrubber that redacts sensitive personal & financial identifiers
    before text is saved, indexed, or forwarded to external AI models.
    """
    
    # Common financial & Indian/global PII regex patterns
    PATTERNS = {
        "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "INDIAN_PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
        "INDIAN_AADHAAR": r"\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b",
        "BANK_ACCOUNT": r"\b\d{9,18}\b",
        "IFSC_CODE": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
        "PHONE_NUMBER": r"\b(?:\+91|0)?[6-9]\d{9}\b|\b\+?1?\d{10}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    }

    @classmethod
    def scrub_text(cls, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Replaces sensitive identifiers with masked tokens and returns redaction stats.
        """
        if not text:
            return "", {}

        scrubbed = text
        stats = {}

        # Scrub Credit Cards first
        cc_matches = re.findall(cls.PATTERNS["CREDIT_CARD"], scrubbed)
        if cc_matches:
            stats["CREDIT_CARD"] = len(cc_matches)
            scrubbed = re.sub(cls.PATTERNS["CREDIT_CARD"], "[REDACTED_CARD]", scrubbed)

        # Scrub PAN
        pan_matches = re.findall(cls.PATTERNS["INDIAN_PAN"], scrubbed, flags=re.IGNORECASE)
        if pan_matches:
            stats["PAN"] = len(pan_matches)
            scrubbed = re.sub(cls.PATTERNS["INDIAN_PAN"], "[REDACTED_PAN]", scrubbed, flags=re.IGNORECASE)

        # Scrub Aadhaar
        aadhaar_matches = re.findall(cls.PATTERNS["INDIAN_AADHAAR"], scrubbed)
        if aadhaar_matches:
            stats["AADHAAR"] = len(aadhaar_matches)
            scrubbed = re.sub(cls.PATTERNS["INDIAN_AADHAAR"], "[REDACTED_AADHAAR]", scrubbed)

        # Scrub Emails
        email_matches = re.findall(cls.PATTERNS["EMAIL"], scrubbed)
        if email_matches:
            stats["EMAIL"] = len(email_matches)
            scrubbed = re.sub(cls.PATTERNS["EMAIL"], "[REDACTED_EMAIL]", scrubbed)

        # Scrub Phone
        phone_matches = re.findall(cls.PATTERNS["PHONE_NUMBER"], scrubbed)
        if phone_matches:
            stats["PHONE"] = len(phone_matches)
            scrubbed = re.sub(cls.PATTERNS["PHONE_NUMBER"], "[REDACTED_PHONE]", scrubbed)

        return scrubbed, stats

pii_scrubber = PIIScrubber()
