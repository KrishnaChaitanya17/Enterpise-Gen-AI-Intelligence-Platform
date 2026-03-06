from app.core.llm_client import get_llm

def llm_verify_claim(claim: str, docs: list) -> dict:
    """
    LLM-based semantic verifier.
    Used when rule-based grounding fails.
    """

    llm = get_llm(temperature=0.0)

    context = "\n\n".join(
        f"Source:\n{doc.page_content}" for doc in docs
    )

    prompt = f"""
You are a strict factual verifier.

Claim:
"{claim}"

Context:
{context}

Answer ONLY with one word:
SUPPORTED or NOT_SUPPORTED
"""

    print("🧠 LLM verifier checking claim:", claim)

    response = llm.invoke(prompt).content.strip().upper()

    return {
        "claim": claim,
        "supported": response == "SUPPORTED",
        "method": "llm",
        "source": docs[0].metadata.get("source") if docs else None
    }
