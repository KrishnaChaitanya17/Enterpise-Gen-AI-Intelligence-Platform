from app.ai.step2_query.rag_chain import run_rag

queries = [
    "How do we handle service outages?",
    "What compensation do engineers get during outages?",
    "What is Kubernetes?",
    "What happens if a service outage is not resolved in 30 minutes?"
]

for q in queries:
    print("\n==============================")
    print("Query:", q)
    result = run_rag(q)
    print("\nAnswer:")
    print(result["answer"])
    print("\nSources:")
    print(result["sources"])
