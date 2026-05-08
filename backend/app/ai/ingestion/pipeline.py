from app.ai.ingestion.multi_loader import load_documents
from app.ai.ingestion.chunker import chunk_documents
from app.ai.ingestion.vector_store import save_vector_db, load_vector_db
from app.ai.ingestion.embedder import load_embeddings

from langchain_community.vectorstores import FAISS


def extract_existing_hashes(vector_db):
    hashes = set()

    try:
        for doc in vector_db.docstore._dict.values():
            h = doc.metadata.get("file_hash")
            if h:
                hashes.add(h)
    except:
        pass

    return hashes


def run_ingestion_pipeline(data_path: str):

    # 🔥 Load existing DB if exists
    try:
        vector_db = load_vector_db()
        existing_hashes = extract_existing_hashes(vector_db)
        print(f"🔁 Existing documents: {len(existing_hashes)}")
    except:
        vector_db = None
        existing_hashes = set()

    docs = load_documents(data_path, existing_hashes)

    if not docs:
        print("⚠️ No new documents to ingest")
        return vector_db

    chunks = chunk_documents(docs)
    print(f"✂️ Chunks created: {len(chunks)}")

    embeddings = load_embeddings()

    if vector_db:
        print("➕ Updating existing vector DB...")
        vector_db.add_documents(chunks)
    else:
        print("🧠 Creating new vector DB...")
        vector_db = FAISS.from_documents(chunks, embeddings)

    save_vector_db(vector_db)

    print("✅ Ingestion complete")

    return vector_db