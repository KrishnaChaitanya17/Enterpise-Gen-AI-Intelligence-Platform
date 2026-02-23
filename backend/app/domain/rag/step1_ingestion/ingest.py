# from app.core.env import *   

# from pathlib import Path
# from langchain_core.documents import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from app.core.llm_config import get_embeddings
# from app.config.settings import OPENAI_API_KEY
# # 
# import os
# print("API BASE:", os.getenv("OPENAI_API_BASE"))
# print("KEY PREFIX:", os.getenv("OPENAI_API_KEY")[:8])


# VECTOR_PATH = "vectorstore/internal_docs"

# def ingest_documents(data_dir: str):
#     documents = []

#     for file in Path(data_dir).glob("*.txt"):
#         try:
#             text = file.read_text(encoding="utf-8", errors="ignore").strip()
#         except Exception as e:
#             print(f"Failed to read {file.name}: {e}")
#             continue

#         if not text:
#             print(f"⚠️ Empty file skipped: {file.name}")
#             continue

#         documents.append(
#             Document(
#                 page_content=text,
#                 metadata={"source": file.name}
#             )
#         )

#     print(f"Valid documents loaded: {len(documents)}")

#     if not documents:
#         raise ValueError("No valid documents found")

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=300,
#         chunk_overlap=50
#     )

#     chunks = splitter.split_documents(documents)

#     print(f"Chunks created: {len(chunks)}")

#     # embeddings = get_embeddings(
#     #     model="text-embedding-3-large",
#     #     api_key=OPENAI_API_KEY
#     # )

#     embeddings = get_embeddings()

#     vector_db = FAISS.load_local(
#         VECTOR_PATH,
#     embeddings,
#     allow_dangerous_deserialization=True
# )

#     # vector_db = FAISS.from_documents(chunks, embeddings)
#     # vector_db.save_local(VECTOR_PATH)

#     print("Vector store saved successfully")

#     return vector_db

from pathlib import Path
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from app.core.embeddings import get_embeddings

VECTOR_PATH = Path("vectorstore/internal_docs")
FAISS_INDEX = VECTOR_PATH / "index.faiss"

def ingest_documents(data_dir: str):
    embeddings = get_embeddings()

    # ✅ Load ONLY if FAISS index exists
    if FAISS_INDEX.exists():
        print("Loading existing vector store...")
        return FAISS.load_local(
            VECTOR_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

    print("Creating new vector store...")

    documents = []
    for file in Path(data_dir).glob("*.txt"):
        try:
            text = file.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception as e:
            print(f"Failed to read {file.name}: {e}")
            continue

        if not text:
            print(f"⚠️ Empty file skipped: {file.name}")
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={"source": file.name}
            )
        )

    if not documents:
        raise ValueError("No valid documents found for ingestion")

    print(f"Valid documents loaded: {len(documents)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)
    print(f"Chunks created: {len(chunks)}")

    vector_db = FAISS.from_documents(chunks, embeddings)

    VECTOR_PATH.mkdir(parents=True, exist_ok=True)
    vector_db.save_local(VECTOR_PATH)

    print("Vector store created and saved.")
    return vector_db
