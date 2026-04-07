def compute_source_quality(sources: list) -> float:
    """
    Simple heuristic:
    More sources = higher confidence
    """

    if not sources:
        return 0.0

    unique_sources = set([s.get("source") for s in sources if s.get("source")])

    return min(len(unique_sources) / 5, 1.0)


def compute_answer_length_score(answer: str) -> float:
    length = len(answer.split())

    if length > 150:
        return 1.0
    elif length > 80:
        return 0.8
    elif length > 30:
        return 0.6
    else:
        return 0.4


def compute_final_scores(answer: str, verification: dict, sources: list) -> dict:

    groundedness = verification.get("groundedness", 0)
    truth_score = verification.get("truth_score", 0)

    source_quality = compute_source_quality(sources)

    # 🧠 Trust Score
    trust_score = (
        0.5 * groundedness +
        0.3 * truth_score +
        0.2 * source_quality
    )

    # 🚨 Hallucination Risk
    hallucination_risk = 1 - groundedness

    # ⭐ Answer Quality
    answer_length_score = compute_answer_length_score(answer)

    answer_quality = (
        0.6 * trust_score +
        0.4 * answer_length_score
    )

    return {
        "trust_score": round(trust_score, 3),
        "hallucination_risk": round(hallucination_risk, 3),
        "answer_quality": round(answer_quality, 3),
        "source_quality": round(source_quality, 3)
    }