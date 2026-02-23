#Check if claims are supported by retrieved docs

def is_claim_supported(claim: str, docs: list) -> dict:
    """
    Check if claim is grounded in any retrieved document.
    """
    claim_lower = claim.lower()

    for doc in docs:
        content = doc.page_content.lower()
        if claim_lower[:20] in content or claim_lower in content:
            return {
                "claim": claim,
                "supported": True,
                "source": doc.metadata.get("source", "unknown")
            }

    return {
        "claim": claim,
        "supported": False,
        "source": None
    }
