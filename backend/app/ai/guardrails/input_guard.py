BANNED_KEYWORDS = {
    "hack": "high",
    "exploit": "high",
    "bypass": "high",
    "steal": "high",
    "attack": "medium"
}


def input_guard(query: str):

    q = query.lower()

    for word, severity in BANNED_KEYWORDS.items():
        if word in q:
            return {
                "blocked": True,
                "reason": f"{severity} risk keyword: {word}",
                "severity": severity
            }

    return {
        "blocked": False,
        "severity": "low"
    }