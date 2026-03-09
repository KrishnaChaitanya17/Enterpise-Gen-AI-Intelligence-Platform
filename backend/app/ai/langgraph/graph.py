from langgraph.graph import StateGraph, END
from typing import TypedDict

from app.ai.langgraph.nodes import generate_node


# -------------------------
# Graph State
# -------------------------
class GraphState(TypedDict, total=False):
    query: str
    answer: str
    verification: str
    confidence: float


# -------------------------
# Build Graph
# -------------------------
builder = StateGraph(GraphState)

builder.add_node("generate", generate_node)

builder.set_entry_point("generate")

builder.add_edge("generate", END)

# -------------------------
# Compile Graph
# -------------------------
graph = builder.compile()