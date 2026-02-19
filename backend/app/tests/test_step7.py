from app.rag.step7_moderation.moderation_runner import run_moderation

query = "How do we handle service outages?"
answer = "During an outage, the on-call engineer responds within 15 minutes."

result = run_moderation(query, answer)
print(result)
