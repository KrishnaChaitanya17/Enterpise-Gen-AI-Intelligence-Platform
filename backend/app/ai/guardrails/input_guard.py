BANNED_KEYWORDS = [
    "hack", "exploit", "bypass", "steal", "attack"
]

def input_guard(query: str):

    q = query.lower()

    for word in BANNED_KEYWORDS:
        if word in q:
            return {
                "blocked": True,
                "reason": f"Blocked due to unsafe keyword: {word}"
            }

    return {
        "blocked": False
    }