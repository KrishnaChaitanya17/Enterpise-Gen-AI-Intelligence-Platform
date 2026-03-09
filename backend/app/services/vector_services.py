import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorService:

    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.index = faiss.IndexFlatL2(384)
        self.documents = []

    def add_documents(self, docs):

        embeddings = self.model.encode(docs)
        embeddings = np.array(embeddings).astype("float32")

        self.index.add(embeddings)
        self.documents.extend(docs)

    def search(self, query, k=3):

        q_embedding = self.model.encode([query])
        q_embedding = np.array(q_embedding).astype("float32")

        distances, indices = self.index.search(q_embedding, k)

        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])

        return results


vector_service = VectorService()