from app.ai.verification.verifier_agent import verify_answer
from app.ai.retrieval.hybrid_retriever import hybrid_search, extract_filters
from app.core.llm_provider import get_llm
from app.core.llm_executor import safe_llm_call
from app.ai.router.model_router import route_model
from app.ai.evaluation.scoring import compute_final_scores


async def run_rag(query: str, filters: dict = None, trace_id=None):

    # ✅ Extract filters
    filters = extract_filters(query)

    # ✅ Retrieve docs
    all_docs = hybrid_search(query, k=5, filters=filters)

    # ✅ Build context
    context = "\n\n".join(
        [d.page_content for d in all_docs[:5]]
    )

    prompt = f"""
You are a helpful AI assistant.

Context:
{context}

Question:
{query}
"""

    # ✅ Model routing
    models = route_model(query)
    llms = get_llm(models, query)

    response = await safe_llm_call(llms, prompt, trace_id)

    answer = response.content

    # ✅ Build sources FIRST (FIXED ORDER)
    sources = []
    for d in all_docs[:5]:
        sources.append({
            "source": d.metadata.get("source"),
            "type": d.metadata.get("type"),
            "created_at": d.metadata.get("created_at")
        })

    # ✅ Verification
    verification = await verify_answer(
        query,
        answer,
        all_docs
    )

    # ✅ Compute scores (NOW SAFE)
    final_scores = compute_final_scores(
        answer,
        verification,
        sources
    )

    confidence = verification.get("confidence", 0.3)

    return {
        "answer": answer,
        "sources": sources,
        "verification": verification,
        "scores": final_scores,
        "confidence": confidence
    }