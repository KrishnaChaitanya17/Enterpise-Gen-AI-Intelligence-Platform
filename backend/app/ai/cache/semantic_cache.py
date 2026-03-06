from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# vector store
dimension = 384
index = faiss.IndexFlatL2(dimension)

cache_questions = []
cache_answers = []


def search_cache(query, threshold=0.85):

    if len(cache_questions) == 0:
        return None

    embedding = model.encode([query])
    D, I = index.search(np.array(embedding).astype("float32"), 1)

    similarity = 1 / (1 + D[0][0])

    if similarity > threshold:
        return cache_answers[I[0][0]]

    return None


def add_to_cache(query, answer):

    embedding = model.encode([query])

    index.add(np.array(embedding).astype("float32"))

    cache_questions.append(query)
    cache_answers.append(answer)