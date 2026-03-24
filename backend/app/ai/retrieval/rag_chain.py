from app.core.llm_client import get_llm
from app.ai.verification.verifier_agent import verify_answer
from app.ai.retrieval.hybrid_retriever import hybrid_search, extract_filters

async def run_rag(query: str, filters: dict = None):

    # 1️⃣ Retrieve documents
    filters = extract_filters(query)
    all_docs = hybrid_search(query, k=5, filters=filters)

    # 2️⃣ Prepare context
    context = "\n\n".join(
        [d.page_content for d in all_docs[:5]]
    )

    # 3️⃣ Prompt
    prompt = f"""
You are a helpful AI assistant.

Context:
{context}

Question:
{query}
"""

    # 4️⃣ Generate answer
    llm = get_llm(query)
    response = await llm.ainvoke(prompt)

    # ✅ 5️⃣ VERIFY (THIS WAS MISSING)
    verification = verify_answer(
        query,
        response.content,
        all_docs
    )

    # ✅ 6️⃣ Confidence from verifier
    confidence = verification.get("confidence", 0.3)

    # 7️⃣ Sources
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
        "confidence": confidence
    }