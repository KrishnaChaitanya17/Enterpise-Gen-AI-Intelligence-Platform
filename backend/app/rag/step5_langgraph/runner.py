from app.rag.step5_langgraph.graph import build_graph

def run_langgraph(query: str):
    graph = build_graph()
    return graph.invoke({"query": query})
