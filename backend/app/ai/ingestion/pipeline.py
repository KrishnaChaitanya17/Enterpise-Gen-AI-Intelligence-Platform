from app.ai.ingestion.multi_loader import load_documents
from app.ai.ingestion.chunker import chunk_documents
from app.ai.ingestion.vector_store import save_vector_db
from app.ai.ingestion.embedder import load_embeddings
import os

from langchain_community.vectorstores import FAISS


def run_ingestion_pipeline(data_path: str):

    print(f"📂 Path received: {data_path}")

    docs = load_documents(data_path)
    
    print("\n================ DEBUG START ================")
    print("📂 Folder path:", data_path)
    print("📂 Files in folder:", os.listdir(data_path))
    print("📄 Documents loaded:", len(docs))

    if len(docs) > 0:
        print("🧾 First doc preview:", docs[0].page_content[:200])
    else:
        print("❌ NO DOCUMENTS LOADED")

    print("================ DEBUG END ================\n")

    # if not docs:
    #     raise ValueError("❌ No documents loaded. Check path or files.")

    chunks = chunk_documents(docs)
    print(f"✂️ Chunks created: {len(chunks)}")

    # if not chunks:
    #     raise ValueError("❌ Chunking failed. No chunks created.")

    embeddings = load_embeddings()

    print("🧠 Creating vector DB...")

    vector_db = FAISS.from_documents(chunks, embeddings)

    save_vector_db(vector_db)

    print("✅ Ingestion complete")

    return vector_db