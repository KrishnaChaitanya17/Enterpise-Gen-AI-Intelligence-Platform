#Check if claims are supported by retrieved docs

from sentence_transformers import SentenceTransformer
import numpy as np

# 🔹 Load once (global, cached)
_model = SentenceTransformer("all-MiniLM-L6-v2")


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def keyword_overlap_score(a: str, b: str) -> float:
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())

    if not a_words:
        return 0.0

    return len(a_words & b_words) / len(a_words)


def semantic_score(a: str, b: str) -> float:
    emb1 = _model.encode(a)
    emb2 = _model.encode(b)

    return cosine_similarity(emb1, emb2)


def is_claim_supported(claim: str, docs: list) -> dict:
    """
    Phase 3.2: Hybrid Grounding (Keyword + Semantic)
    """

    best_score = 0
    best_source = None
    best_method = "none"

    for doc in docs:
        content = doc.page_content

        # 🔹 keyword score
        k_score = keyword_overlap_score(claim, content)

        # 🔹 semantic score
        s_score = semantic_score(claim, content)

        # 🔥 hybrid score
        final_score = (0.5 * k_score) + (0.5 * s_score)

        if final_score > best_score:
            best_score = final_score
            best_source = doc.metadata.get("source", "unknown")

            if s_score > k_score:
                best_method = "semantic"
            else:
                best_method = "keyword"

    # -----------------------------
    # 🎯 THRESHOLDS
    # -----------------------------
    if best_score >= 0.75:
        return {
            "claim": claim,
            "supported": True,
            "score": 1.0,
            "source": best_source,
            "method": f"strong_{best_method}"
        }

    elif best_score >= 0.5:
        return {
            "claim": claim,
            "supported": True,
            "score": 0.7,
            "source": best_source,
            "method": f"partial_{best_method}"
        }

    elif best_score >= 0.3:
        return {
            "claim": claim,
            "supported": False,
            "score": 0.3,
            "source": best_source,
            "method": "weak_match"
        }

    else:
        return {
            "claim": claim,
            "supported": False,
            "score": 0.0,
            "source": None,
            "method": "no_match"
        }