import re

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+system\s+prompt",
    r"you\s+are\s+now",
    r"act\s+as",
    r"pretend\s+to\s+be",
    r"bypass\s+security",
    r"reveal\s+hidden\s+prompt"
]


def detect_prompt_injection(query: str):

    q = query.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, q):
            return True

    return False