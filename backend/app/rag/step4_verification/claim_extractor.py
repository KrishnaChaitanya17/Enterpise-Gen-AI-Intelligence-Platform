#Break answer into factual claims

def extract_claims(answer: str) -> list[str]:
    """
    Split the answer into atomic factual claims.
    Simple sentence-based splitting (safe & explainable).
    """
    sentences = answer.split(".")
    claims = [s.strip() for s in sentences if s.strip()]
    return claims
