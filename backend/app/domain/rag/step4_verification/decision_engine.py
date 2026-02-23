#Decide what user finally sees

from app.rag.step4_verification.grounding_checker import is_claim_supported


def evaluate_claims(claims: list[str], docs: list) -> list[dict]:
    """
    Evaluate each claim against retrieved documents.
    """
    results = []

    for claim in claims:
        result = is_claim_supported(claim, docs)
        results.append(result)

    return results


def finalize_response(answer: str, verification: dict) -> dict:
    verdict = verification["verdict"]

    if verdict == "ALL_SUPPORTED":
        return {
            "answer": answer,
            "confidence": "high",
            "verification": verification
        }

    if verdict == "PARTIALLY_SUPPORTED":
        return {
            "answer": (
                "⚠️ The following answer is partially supported by the knowledge base:\n\n"
                + answer
            ),
            "confidence": "medium",
            "verification": verification
        }

    return {
        "answer": (
            "❌ I cannot verify this answer with the available documents. "
            "Please rephrase or provide more context."
        ),
        "confidence": "low",
        "verification": verification
    }
