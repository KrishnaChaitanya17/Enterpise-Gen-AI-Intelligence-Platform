from langchain_community.vectorstores import FAISS
from app.ai.ingestion.embedder import load_embeddings
import os

VECTOR_DB_PATH = "vectorstore/internal_docs"


def save_vector_db(vector_db, path: str = VECTOR_DB_PATH):
    os.makedirs(path, exist_ok=True)
    vector_db.save_local(path)


def load_vector_db(path: str = VECTOR_DB_PATH):
    embeddings = load_embeddings()

    if not os.path.exists(path):
        return None

    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )


# 🔥 NEW: Incremental Add
def add_documents_to_vector_db(new_docs, path: str = VECTOR_DB_PATH):

    embeddings = load_embeddings()

    # 1️⃣ Load existing DB
    if os.path.exists(path):
        vector_db = load_vector_db(path)

        # 2️⃣ Get existing chunk_ids
        existing_ids = set()
        existing_hash_map = {}

        if vector_db and vector_db.docstore:
            for _, doc in vector_db.docstore._dict.items():
                doc_id = doc.metadata.get("document_id")
                file_hash = doc.metadata.get("file_hash")
                version = doc.metadata.get("version",1)

                if doc_id:
                    existing_hash_map[doc_id] = {
                        "hash": file_hash,
                        "version": version
                    }

        filtered_docs = []
        
        for d in new_docs:
            doc_id = d.metadata.get("document_id")
            new_hash = d.metadata.get("file_hash")

            existing = existing_hash_map.get(doc_id)

            # 🟢 NEW FILE
            if not existing:
                filtered_docs.append(d)
                continue

            # 🟡 SAME FILE (no change)
            if existing["hash"] == new_hash:
                continue

            # 🔴 UPDATED FILE → increase version
            new_version = existing["version"] + 1
            d.metadata["version"] = new_version

            filtered_docs.append(d)

    else:
        print("📦 Creating new vector DB")
        vector_db = FAISS.from_documents(new_docs, embeddings)

    # 5️⃣ Save updated DB
    save_vector_db(vector_db, path)

    return vector_db