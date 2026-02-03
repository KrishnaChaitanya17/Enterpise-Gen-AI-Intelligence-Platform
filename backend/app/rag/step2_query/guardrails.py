def validate_answer(answer: str, docs: list) -> str:
    if not answer or len(answer.strip()) < 10:
        return "The provided documents do not contain enough information."

    forbidden_phrases = [
        "I think",
        "probably",
        "might be",
        "in general",
        "usually",
        "based on my knowledge"
    ]

    for phrase in forbidden_phrases:
        if phrase.lower() in answer.lower():
            return "The provided documents do not contain enough information."

    # Ensure at least one source is referenced
    sources = [doc.metadata.get("source", "") for doc in docs]
    if not any(src in answer for src in sources):
        return "The provided documents do not contain enough information."

    return answer
