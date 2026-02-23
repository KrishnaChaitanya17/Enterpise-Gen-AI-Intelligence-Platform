from langgraph.graph import StateGraph, END
from app.rag.step5_langgraph.state import RAGState
from app.rag.step5_langgraph.nodes import generate_node, regenerate_node

def build_graph():
    graph = StateGraph(RAGState)

    graph.add_node("generate", generate_node)
    graph.add_node("regenerate", regenerate_node)

    graph.set_entry_point("generate")

    graph.add_conditional_edges(
        "generate",
        lambda state: state["confidence"],
        {
            "high": END,
            "medium": "regenerate",
            "low": "regenerate",
        }
    )

    graph.add_edge("regenerate", END)

    return graph.compile()
