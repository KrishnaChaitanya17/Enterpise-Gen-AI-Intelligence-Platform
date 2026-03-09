from langgraph.graph import StateGraph, END
from app.ai.moderation.langgraph.state import ModerationState
from app.ai.moderation.langgraph.nodes import (
    moderation_node,
    redaction_node,
    human_review_node,
    finalize_node,
)


def build_moderation_graph():

    graph = StateGraph(ModerationState)

    graph.add_node("moderation", moderation_node)
    graph.add_node("redaction", redaction_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("finalize", finalize_node)

    graph.set_entry_point("moderation")

    def route_decision(state):
        verdict = state["final_verdict"]

        if verdict == "REDACT":
            return "redaction"
        elif verdict == "REVIEW":
            return "human_review"
        else:
            return "finalize"

    graph.add_conditional_edges(
        "moderation",
        route_decision,
        {
            "redaction": "redaction",
            "human_review": "human_review",
            "finalize": "finalize",
        },
    )

    graph.add_edge("redaction", "finalize")
    graph.add_edge("human_review", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()
