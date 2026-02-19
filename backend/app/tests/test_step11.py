from app.rag.step10_evidence_engine.aggregator import aggregate_evidence
from app.rag.step11_decision_reasoning.reasoning_orchestrator import run_decision_reasoning

verification = {"verdict": "ALL_SUPPORTED"}
evaluation = {"groundedness": 1.0, "confidence": "high"}
moderation = {"final_verdict": "ALLOW"}

evidence = aggregate_evidence(verification, evaluation, moderation)

decision = run_decision_reasoning(evidence)

print(decision)
