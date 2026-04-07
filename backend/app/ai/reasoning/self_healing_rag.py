from app.core.llm_provider import get_llm
from app.core.llm_executor import safe_llm_call
from app.ai.router.model_router import route_model


async def retry_with_reasoning(
    query: str,
    rag_answer: str,
    verification: dict,
    trace_id: str = None
) -> str:

    # ✅ If already good → return
    if verification.get("verdict") == "SUPPORTED":
        return rag_answer

    retry_prompt = f"""
You are an expert AI system improving a weak or incorrect answer.

Rules:
- Fix factual errors
- Be clear and concise
- Do NOT hallucinate
- If unsure, say "I’m not fully certain"

Question:
{query}

Previous Answer:
{rag_answer}

Return a better, accurate answer.
"""

    models = route_model(query)

    # 🔥 Use multi-model system
    llms = get_llm(models, query)

    improved = await safe_llm_call(llms, retry_prompt, trace_id)

    return improved.content if hasattr(improved, "content") else rag_answer