#MMR (Max Marginal Relevance)

from sklearn.metrics.pairwise import cosine_similarity

def mmr(query_emb, doc_embs, docs, k=5, lambda_param=0.7):
    selected = []
    selected_embs = []

    while docs and len(selected) < k:
        scores = []
        for i, emb in enumerate(doc_embs):
            relevance = cosine_similarity([query_emb], [emb])[0][0]
            diversity = 0
            if selected_embs:
                diversity = max(
                    cosine_similarity([emb], selected_embs)[0]
                )
            score = lambda_param * relevance - (1 - lambda_param) * diversity
            scores.append((i, score))

        best = max(scores, key=lambda x: x[1])[0]
        selected.append(docs.pop(best))
        selected_embs.append(doc_embs.pop(best))

    return selected
