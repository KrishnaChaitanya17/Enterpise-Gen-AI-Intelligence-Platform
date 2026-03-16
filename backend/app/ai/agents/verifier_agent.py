def verify_answer(answer: str):

    if not answer:
        return {
            "verified": False,
            "confidence": 0.2
        }

    if len(answer) < 20:
        return {
            "verified": False,
            "confidence": 0.4
        }

    return {
        "verified": True,
        "confidence": 0.9
    }