from app.ai.verification.verifier_agent import verify_answer
from app.ai.retrieval.hybrid_retriever import hybrid_search, extract_filters
from app.core.llm_provider import get_llm
from app.core.llm_executor import safe_llm_call
from app.ai.router.model_router import route_model
from app.ai.evaluation.scoring import compute_final_scores

async def run_rag(query: str, filters: dict = None, trace_id=None):

    filters = extract_filters(query)
    all_docs = hybrid_search(query, k=5, filters=filters)

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

    # ✅ FIX
    models = route_model(query)
    llms = get_llm(models, query)

    response = await safe_llm_call(llms, prompt, trace_id)

    # ✅ VERIFY
    verification = await verify_answer(
        query,
        response.content,
        all_docs
    )

    final_scores = compute_final_scores(
    response.content,
    verification,
    sources
    )

    confidence = verification.get("confidence", 0.3)

    sources = []
    for d in all_docs[:5]:
        sources.append({
            "source": d.metadata.get("source"),
            "type": d.metadata.get("type"),
            "created_at": d.metadata.get("created_at")
        })

    return {
        "answer": response.content,
        "sources": sources,
        "verification": verification,
        # New System Output
        "scores" : final_scores,
        #backward compatibility
        "confidence": verification.get("confidence", 0.3) 
    }