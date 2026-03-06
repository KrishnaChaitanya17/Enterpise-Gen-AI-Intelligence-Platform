# This is what we call after Step 5 finishes.
# Entry point for Step 6

# Called once per completed query

# Builds a structured evaluation record

from datetime import datetime
from app.ai.evaluation.schemas import EvaluationResult
from app.ai.evaluation.metrics import (
    compute_groundedness,
    was_regenerated,
)
from app.ai.evaluation.feedback_store import save_evaluation


def evaluate_response(
    query: str,
    answer: str,
    verification: dict,
    confidence,
    sources: list,
):

    # -----------------------------
    # GROUNDEDNESS
    # -----------------------------
    groundedness = compute_groundedness(verification)

    # -----------------------------
    # RETRIEVAL DOC COUNT
    # -----------------------------
    retrieval_doc_count = len(
        {c.get("source") for c in verification.get("checks", []) if c.get("source")}
    )

    # -----------------------------
    # REGENERATION CHECK
    # -----------------------------
    regenerated = was_regenerated(confidence)

    # -----------------------------
    # QUALITY SCORE
    # -----------------------------
    quality_score = (
        groundedness * 0.6
        + min(retrieval_doc_count / 5, 1.0) * 0.2
        + (0 if regenerated else 1) * 0.2
    )

    # -----------------------------
    # BUILD RESULT OBJECT
    # -----------------------------
    result = EvaluationResult(
        query=query,
        answer=answer,
        confidence=str(confidence),
        verdict=verification.get("verdict"),
        groundedness_score=groundedness,
        retrieval_doc_count=retrieval_doc_count,
        regenerated=regenerated,
        quality_score=quality_score,
        timestamp=datetime.utcnow(),
    )

    # -----------------------------
    # SAVE FOR ANALYTICS
    # -----------------------------
    save_evaluation(result)

    return result