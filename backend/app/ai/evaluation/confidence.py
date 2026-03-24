def calculate_confidence(answer: str, context: str = None):

    if not answer:
        return 0.0

    length_score = min(len(answer) / 200, 1)

    context_score = 0.5 if context else 0.2

    keyword_overlap = 0.5
    if context and answer:
        a = set(answer.lower().split())
        c = set(context.lower().split())
        keyword_overlap = len(a & c) / max(len(a), 1)

    final_score = (0.4 * length_score) + (0.3 * context_score) + (0.3 * keyword_overlap)

    return round(final_score, 2)