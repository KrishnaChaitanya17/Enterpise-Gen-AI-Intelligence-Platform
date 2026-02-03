from app.rag.step1_ingestion.vector_store import load_vector_db

def retrieve_docs(query: str, k: int = 3):
    vectorstore = load_vector_db()
    return vectorstore.similarity_search(query, k=k)
