from app.rag.step2_query.rag_chain import run_rag

print(run_rag("How do we handle service outages?")["answer"])
print(run_rag("What happens if it is not resolved in time?")["answer"])
