from app.ai.reasoning.evidence.schemas import EvidenceBundle
from app.ai.reasoning.evidence.risk_scoring import compute_risk


def aggregate_evidence(
    verification_result: dict,
    evaluation_result: dict,
    moderation_result: dict
) -> EvidenceBundle:

    # Extract truth score
    truth_score = 1.0 if verification_result.get("verdict") == "ALL_SUPPORTED" else 0.5

    groundedness = evaluation_result.get("groundedness", 1.0)

    moderation_status = moderation_result.get("final_verdict", "ALLOW")

    confidence = evaluation_result.get("confidence", "medium")

    risk_score = compute_risk(truth_score, moderation_status, groundedness)

    metadata = {
        "verification": verification_result,
        "evaluation": evaluation_result,
        "moderation": moderation_result
    }

    return EvidenceBundle(
        truth_score=truth_score,
        groundedness=groundedness,
        moderation_status=moderation_status,
        risk_score=risk_score,
        confidence=confidence,
        metadata=metadata
    )
