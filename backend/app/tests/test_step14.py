from app.rag.step14_enterprise.pipeline import run_enterprise_pipeline

verification = {"verdict": "ALL_SUPPORTED"}
evaluation = {"groundedness": 1.0, "confidence": "high"}
moderation = {"final_verdict": "ALLOW"}

result = run_enterprise_pipeline(
    verification=verification,
    evaluation=evaluation,
    moderation=moderation,
)

print("\n🚀 ENTERPRISE STEP 14 RESULT:\n")
print(result)
