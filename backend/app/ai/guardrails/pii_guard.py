import re

PII_PATTERNS = {
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "phone": r"\b\d{10}\b",
    "credit_card": r"\b\d{16}\b"
}


def detect_pii(text: str):
    found = []

    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            found.append((pii_type, matches))

    return found


def mask_pii(text: str):
    detected = detect_pii(text)

    for pattern in PII_PATTERNS.values():
        text = re.sub(pattern, "[REDACTED]", text)

    return text, detected