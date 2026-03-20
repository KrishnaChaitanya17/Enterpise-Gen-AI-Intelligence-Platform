from app.ai.ingestion.vector_store import load_vector_db
from langchain.retrievers import BM25Retriever
from datetime import datetime, timedelta


def keyword_overlap(query: str, text: str) -> float:
    q = set(query.lower().split())
    t = set(text.lower().split())
    return len(q & t) / max(len(q), 1)


def get_hybrid_retriever():

    vector_db = load_vector_db()

    # 1️⃣ Get ALL documents (for BM25)
    all_docs = vector_db.similarity_search("", k=1000)  # ⚠️ temp approach

    # 2️⃣ Create BM25 on full corpus
    bm25 = BM25Retriever.from_documents(all_docs)
    bm25.k = 5

    # 3️⃣ Vector retriever
    vector_retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    return vector_retriever, bm25


def hybrid_search(query: str, k: int = 5, filters: dict = None):

    vector_retriever, bm25 = get_hybrid_retriever()

    vector_docs = vector_retriever.invoke(query)
    bm25_docs = bm25.invoke(query)

    all_docs = vector_docs + bm25_docs

    # 🔥 Apply filters BEFORE scoring
    all_docs = apply_filters(all_docs, filters)

    scored = []

    for d in all_docs:
        keyword_score = keyword_overlap(query, d.page_content)
        scored.append((d, keyword_score))

    scored.sort(key=lambda x: x[1], reverse=True)

    seen = set()
    final_docs = []

    for d, _ in scored:
        if d.page_content not in seen:
            seen.add(d.page_content)
            final_docs.append(d)

        if len(final_docs) >= k:
            break

    return final_docs

def apply_filters(docs, filters: dict):

    if not filters:
        return docs

    filtered = []

    for d in docs:
        meta = d.metadata

        # Filter by type
        if filters.get("type"):
            if meta.get("type") != filters["type"]:
                continue

        # Filter by source
        if filters.get("source"):
            if filters["source"].lower() not in meta.get("source", "").lower():
                continue

        # Filter by recent (in days)
        if filters.get("recent_days"):
            created_at = meta.get("created_at")
            if created_at:
                doc_time = datetime.fromisoformat(created_at)
                if doc_time < datetime.utcnow() - timedelta(days=filters["recent_days"]):
                    continue

        filtered.append(d)

    return filtered

def extract_filters(query: str):

    filters = {}

    q = query.lower()

    if "pdf" in q:
        filters["type"] = "pdf"

    if "csv" in q:
        filters["type"] = "csv"

    if "recent" in q or "latest" in q:
        filters["recent_days"] = 7

    return filters