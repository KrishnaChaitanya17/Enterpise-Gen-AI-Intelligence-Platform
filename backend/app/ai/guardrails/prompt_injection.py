INJECTION_PATTERNS = [
    "ignore previous instructions",
    "disregard system prompt",
    "you are now",
    "act as",
    "pretend to be"
]

def detect_prompt_injection(query: str):

    q = query.lower()

    for pattern in INJECTION_PATTERNS:
        if pattern in q:
            return True

    return False