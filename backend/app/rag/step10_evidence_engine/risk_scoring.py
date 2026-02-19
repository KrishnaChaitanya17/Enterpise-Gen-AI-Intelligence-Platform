def compute_risk(truth_score: float, moderation_status: str, groundedness: float) -> float:
    risk = 0.0

    # Penalize low truth score
    if truth_score < 0.7:
        risk += 0.4

    # Penalize low groundedness
    if groundedness < 0.7:
        risk += 0.3

    # High penalty if moderation flagged
    if moderation_status in ["BLOCK", "REVIEW"]:
        risk += 0.5

    return min(risk, 1.0)
