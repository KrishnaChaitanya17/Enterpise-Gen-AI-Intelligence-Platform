def verify_answer(answer):

    if not isinstance(answer, str):
        answer = str(answer)

    if len(answer) < 20:
        return {
            "verdict": "LOW_QUALITY",
            "confidence": "low",
            "checks": [
                {"check": "length", "supported": False}
            ]
        }

    return {
        "verdict": "GOOD",
        "confidence": "high",
        "checks": [
            {"check": "length", "supported": True}
        ]
    }