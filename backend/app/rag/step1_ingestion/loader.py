from langchain.document_loaders import PyPDFLoader
from pathlib import Path

def load_documents(folder_path: str):
    documents = []
    for file in Path(folder_path).glob("*.pdf"):
        loader = PyPDFLoader(str(file))
        docs = loader.load()
        documents.extend(docs)
    return documents