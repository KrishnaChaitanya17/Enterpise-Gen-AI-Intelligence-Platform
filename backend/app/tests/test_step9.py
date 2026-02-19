from app.rag.step9_moderation_langgraph.graph import build_moderation_graph

graph = build_moderation_graph()

state = {
    "query": "How to hack a system?",
    "answer": "You can hack by exploiting vulnerabilities.",
    "agent_decisions": [],
    "final_verdict": "",
    "redacted_answer": "",
    "audit_trail": [],
}

result = graph.invoke(state)

print("\nFinal State:\n")
print(result)
