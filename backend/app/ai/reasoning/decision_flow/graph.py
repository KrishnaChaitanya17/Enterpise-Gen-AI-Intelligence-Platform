from langgraph.graph import StateGraph, END
from backend.app.ai.reasoning.decision_flow.state import DecisionState
from backend.app.ai.reasoning.decision_flow.nodes import (
    reasoning_node,
    execution_node,
    escalation_node,
    rejection_node,
    finalize_node,
)


def build_decision_graph():

    graph = StateGraph(DecisionState)

    graph.add_node("reasoning", reasoning_node)
    graph.add_node("execute", execution_node)
    graph.add_node("escalate", escalation_node)
    graph.add_node("reject", rejection_node)
    graph.add_node("finalize", finalize_node)

    graph.set_entry_point("reasoning")

    def route(state):
        op_decision = state["final_decision"]["operational_decision"]

        if op_decision == "APPROVE":
            return "execute"
        elif op_decision == "INVESTIGATE":
            return "escalate"
        else:
            return "reject"

    graph.add_conditional_edges(
        "reasoning",
        route,
        {
            "execute": "execute",
            "escalate": "escalate",
            "reject": "reject",
        },
    )

    graph.add_edge("execute", "finalize")
    graph.add_edge("escalate", "finalize")
    graph.add_edge("reject", "finalize")

    graph.add_edge("finalize", END)

    return graph.compile()
