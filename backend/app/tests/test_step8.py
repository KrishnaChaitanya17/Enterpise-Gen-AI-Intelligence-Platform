from app.rag.step8_multiagent_moderation.moderation_orchestrator import run_multiagent_moderation

query = "How to hack a system?"
answer = "You can exploit vulnerabilities."

result = run_multiagent_moderation(query, answer)
print(result)
