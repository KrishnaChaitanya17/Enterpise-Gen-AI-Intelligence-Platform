from backend.app.ai.reasoning.evidence.aggregator import aggregate_evidence
from backend.app.ai.reasoning.decision_flow.graph import build_decision_graph

verification = {"verdict": "ALL_SUPPORTED"}
evaluation = {"groundedness": 1.0, "confidence": "high"}
moderation = {"final_verdict": "ALLOW"}

evidence = aggregate_evidence(verification, evaluation, moderation)

graph = build_decision_graph()

state = {
    "evidence": evidence,
    "final_decision": {},
    "execution_status": "",
    "audit_trail": [],
}

result = graph.invoke(state)

print("\nFinal Decision Workflow Result:\n")
print(result)
