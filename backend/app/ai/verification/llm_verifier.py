from app.core.llm_provider import get_llm
from app.core.llm_executor import safe_llm_call
from app.ai.router.model_router import route_model


async def llm_verify_claim(claim: str, docs: list, trace_id=None) -> dict:

    context = "\n\n".join(
        f"Source:\n{doc.page_content}" for doc in docs[:3]
    )

    prompt = f"""
You are a strict factual verifier.

Claim:
"{claim}"

Context:
{context}

Answer ONLY:
SUPPORTED or NOT_SUPPORTED
"""

    models = route_model(claim)
    llms = get_llm(models, claim)

    response = await safe_llm_call(llms, prompt, trace_id)

    result = response.content.strip().upper()

    return {
        "claim": claim,
        "supported": result == "SUPPORTED",
        "method": "llm",
        "source": docs[0].metadata.get("source") if docs else None
    }