def run_enterprise_pipeline(
    verification_result: dict,
    evaluation_result: dict,
    moderation_result: dict
):
    """
    Enterprise-level risk and trust aggregation layer.
    Combines verification, evaluation, and moderation outputs.
    """

    # -----------------------------
    # 1️⃣ Normalize confidence
    # -----------------------------
    confidence_label = verification_result.get("confidence", "low")

    confidence_mapping = {
        "high": 1.0,
        "medium": 0.6,
        "low": 0.3
    }

    confidence = confidence_mapping.get(confidence_label, 0.3)

    # -----------------------------
    # 2️⃣ Extract verification metrics
    # -----------------------------
    truth_score = float(verification_result.get("truth_score", 0.0))
    groundedness = float(verification_result.get("groundedness", 0.0))

    # -----------------------------
    # 3️⃣ Evaluation + Moderation
    # -----------------------------
    quality_score = float(evaluation_result.quality_score)
    risk_score = float(moderation_result.get("risk_score", 0.0))

    # -----------------------------
    # 4️⃣ Weighted enterprise formula
    # -----------------------------
    trust_score = (
        (confidence * 0.25) +
        (truth_score * 0.25) +
        (groundedness * 0.15) +
        (quality_score * 0.20) -
        (risk_score * 0.15)
    )

    trust_score = max(0.0, min(1.0, trust_score))

    if trust_score >= 0.8:
        decision = "HIGH_TRUST"
    elif trust_score >= 0.55:
        decision = "MEDIUM_TRUST"
    else:
        decision = "LOW_TRUST"

    return {
        "trust_score": round(trust_score, 3),
        "decision": decision,
        "confidence": confidence,
        "truth_score": truth_score,
        "groundedness": groundedness,
        "quality_score": quality_score,
        "risk_score": risk_score
    }