from langchain_community.vectorstores import FAISS
from app.rag.step1_ingestion.embedder import get_embeddings
import os

VECTOR_DB_PATH = "vectorstore/internal_docs"


def save_vector_db(vector_db, path: str = VECTOR_DB_PATH):
    os.makedirs(path, exist_ok=True)
    vector_db.save_local(path)


def load_vector_db(path: str = VECTOR_DB_PATH):
    embeddings = get_embeddings()
    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )
