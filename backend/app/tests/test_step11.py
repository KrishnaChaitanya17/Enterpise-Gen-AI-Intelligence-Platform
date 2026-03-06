from backend.app.ai.reasoning.evidence.aggregator import aggregate_evidence
from backend.app.ai.reasoning.reasoning_orchestrator import run_decision_reasoning

verification = {"verdict": "ALL_SUPPORTED"}
evaluation = {"groundedness": 1.0, "confidence": "high"}
moderation = {"final_verdict": "ALLOW"}

evidence = aggregate_evidence(verification, evaluation, moderation)

decision = run_decision_reasoning(evidence)

print(decision)
