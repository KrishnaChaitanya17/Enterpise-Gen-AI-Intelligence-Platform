from app.rag.step5_langgraph.runner import run_langgraph

query = "What is the on-call response time during an outage?"

print(run_langgraph(query))
