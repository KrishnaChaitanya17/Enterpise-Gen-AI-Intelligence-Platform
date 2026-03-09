def finalize_response(answer: str, verification: dict) -> dict:

    verdict = verification.get("verdict")

    if verdict == "ALL_SUPPORTED":
        return {
            "answer": answer,
            "confidence": "high",
            "verification": verification
        }

    if verdict == "PARTIALLY_SUPPORTED":
        return {
            "answer": answer,
            "confidence": "medium",
            "verification": verification
        }

    return {
        "answer": answer,
        "confidence": "low",
        "verification": verification
    }