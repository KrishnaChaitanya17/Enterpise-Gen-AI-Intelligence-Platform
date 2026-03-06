from backend.app.ai.reasoning.evidence.aggregator import aggregate_evidence

verification = {
    "verdict": "ALL_SUPPORTED"
}

evaluation = {
    "groundedness": 1.0,
    "confidence": "high"
}

moderation = {
    "final_verdict": "ALLOW"
}

bundle = aggregate_evidence(verification, evaluation, moderation)

print(bundle)
