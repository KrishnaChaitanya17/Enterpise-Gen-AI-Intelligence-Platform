# from langchain_community.vectorstores import FAISS
# from app.core.embeddings import get_embeddings

# VECTOR_PATH = "vectorstore/internal_docs"

# def get_retriever(k=4, score_threshold=0.7):
#     embeddings = get_embeddings()  # 🔥 HuggingFace ONLY

#     vector_db = FAISS.load_local(
#         VECTOR_PATH,
#         embeddings,
#         allow_dangerous_deserialization=True
#     )

#     return vector_db.as_retriever(
#         search_type="similarity",
#         search_kwargs={
#             "k": k,
#         }
#     )

from app.core.embeddings import get_embeddings
from app.ai.retrieval.hybrid_retriever import hybrid_retrieve
from app.ai.retrieval.mmr import mmr


# ------------------------------------------------
# Retriever Class
# ------------------------------------------------

class HybridMMRRetriever:

    def __init__(self, k: int = 5, fetch_k: int = 15):

        self.k = k
        self.fetch_k = fetch_k
        self.embeddings = get_embeddings()

    def invoke(self, query: str):

        # 1️⃣ Hybrid retrieval
        candidates = hybrid_retrieve(query, fetch_k=self.fetch_k)

        if not candidates:
            return []

        # 2️⃣ Embeddings
        query_emb = self.embeddings.embed_query(query)

        doc_embs = self.embeddings.embed_documents(
            [d.page_content for d in candidates]
        )

        # 3️⃣ MMR reranking
        reranked = mmr(
            query_emb,
            doc_embs,
            candidates,
            k=self.k
        )

        return reranked


# ------------------------------------------------
# Singleton Retriever
# ------------------------------------------------

_retriever = None


def get_retriever(k: int = 5):

    global _retriever

    if _retriever is None:
        _retriever = HybridMMRRetriever(k=k)

    return _retriever


# ------------------------------------------------
# Wrapper used by rag_chain
# ------------------------------------------------

def get_retrieved_docs(query: str, k: int = 5):

    retriever = get_retriever(k)

    docs = retriever.invoke(query)

    return docs