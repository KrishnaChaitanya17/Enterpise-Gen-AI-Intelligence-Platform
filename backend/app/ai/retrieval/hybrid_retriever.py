from app.ai.ingestion.vector_store import load_vector_db

def keyword_overlap(query: str, text: str) -> float:
    q = set(query.lower().split())
    t = set(text.lower().split())
    return len(q & t) / max(len(q), 1)

def hybrid_retrieve(query: str, fetch_k: int = 15):
    vector_db = load_vector_db()
    docs = vector_db.similarity_search(query, k=fetch_k)

    scored = []
    for d in docs:
        score = keyword_overlap(query, d.page_content)
        scored.append((d, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [d for d, _ in scored]