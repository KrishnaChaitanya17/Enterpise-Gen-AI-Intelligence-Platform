from app.core.llm_client import get_llm
from app.ai.verification.verifier_agent import verify_answer
from app.ai.retrieval.source_formatter import format_sources
from app.ai.retrieval.hybrid_retriever import hybrid_search, extract_filters

async def run_rag(query: str, filters: dict = None):

    # 1️⃣ Retrieve documents
    filters = extract_filters(query)
    all_docs = hybrid_search(query, k=5, filters=filters)

    # 2️⃣ Prepare context
    context = "\n\n".join(
        [d.page_content for d in all_docs[:5]]
    )

    # 3️⃣ Build prompt
    prompt = f"""
You are a helpful AI assistant.

Answer the question clearly and concisely.

Context:
{context}

Question:
{query}

If the answer is not fully in the context, use your general knowledge.
"""

    # 4️⃣ Generate answer
    llm = get_llm(query)
    response = await llm.ainvoke(prompt)   # 🔥 async version

    # Format sources cleanly
    sources = []
    for d in all_docs[:5]:
        sources.append({
            "source": d.metadata.get("source"),
            "type": d.metadata.get("type"),
            "created_at": d.metadata.get("created_at")
        })

    print("CONTEXT:", context)
    print("QUERY:", query)
    print("ANSWER:", response.content)

    return {
        "answer": response.content,
        "sources": sources
    }