# This is what we call after Step 5 finishes.
# Entry point for Step 6

# Called once per completed query

# Builds a structured evaluation record

from datetime import datetime
from app.rag.step6_evaluation.schemas import EvaluationResult
from app.rag.step6_evaluation.metrics import (
    compute_groundedness,
    was_regenerated,
)
from app.rag.step6_evaluation.feedback_store import save_evaluation


def evaluate_response(
    query: str,
    answer: str,
    verification: dict,
    confidence: str,
    sources: list,
):
    result = EvaluationResult(
    query=query,
    answer=answer,
    confidence=confidence,
    verdict=verification.get("verdict"),
    groundedness_score=compute_groundedness(verification),
    retrieval_doc_count=len(
        {c.get("source") for c in verification.get("checks", []) if c.get("source")}
    ),
    regenerated=was_regenerated(confidence),
    timestamp=datetime.utcnow(),
)

    save_evaluation(result)

    return result
