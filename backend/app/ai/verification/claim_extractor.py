#Break answer into factual claims

def extract_claims(answer: str) -> list[str]:
    """
    Split the answer into atomic factual claims.
    Simple sentence-based splitting (safe & explainable).
    """
    sentences = answer.replace("\n", " ").split(".")

    claims = [
        s.strip()
        for s in sentences
        if (
            len(s.strip()) > 15
            and not s.strip().isdigit()
            and len(s.split()) > 3   # avoid junk like "Yes it is"
        )
    ]

    return claims