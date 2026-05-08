import os
import uuid
from datetime import datetime
import hashlib

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader
)

def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_documents(folder_path, existing_hashes=None):
    documents = []
    existing_hashes = existing_hashes or set()

    print(f"📂 Reading folder: {folder_path}")

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        try:
            file_hash = get_file_hash(file_path)

            # 🔥 SKIP unchanged files
            if file_hash in existing_hashes:
                print(f"⏩ Skipping unchanged file: {file}")
                continue

            # Detect file type
            if file.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                file_type = "pdf"

            elif file.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
                file_type = "txt"

            elif file.endswith(".csv"):
                loader = CSVLoader(file_path)
                file_type = "csv"

            elif file.endswith(".docx"):
                loader = UnstructuredWordDocumentLoader(file_path)
                file_type = "docx"

            else:
                continue

            docs = loader.load()

            timestamp = datetime.utcnow().isoformat()
            document_id = file

            for i, doc in enumerate(docs):
                doc.metadata.update({
                    "source": file,
                    "type": file_type,
                    "created_at": timestamp,
                    "document_id": document_id,
                    "chunk_id": f"{document_id}_{i}",
                    "file_hash": file_hash,
                    "version": 1
                })

            documents.extend(docs)

        except Exception as e:
            print(f"❌ ERROR in {file}: {e}")

    return documents