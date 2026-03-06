# step 5
# from app.rag.step5_langgraph.graph import build_graph

# def run_langgraph(query: str):
#     graph = build_graph()
#     return graph.invoke({"query": query})

# for step 6

from app.ai.langgraph.graph import build_graph
from app.ai.evaluation.evaluator import evaluate_response  # ✅ ADD

def run_langgraph(query: str):
    graph = build_graph()

    # Step 5 execution
    result = graph.invoke({"query": query})

    # 🔵 STEP 6: Evaluation & Feedback (non-blocking)
    evaluate_response(
        query=query,
        answer=result.get("answer"),
        verification=result.get("verification"),
        confidence=result.get("confidence"),
        sources=result.get("sources", []),
    )

    # Return unchanged response to user
    return result
