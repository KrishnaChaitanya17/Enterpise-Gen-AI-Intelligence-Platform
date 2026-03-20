from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

# existing logic
from app.ai.retrieval.rag_chain import run_rag
from app.ai.reasoning.reasoning_orchestrator import run_decision_reasoning

# reuse your old agent logic
from app.ai.agents.router_agent import route_query
from app.ai.agents.tool_agent import tool_agent


# ---------------- STATE ----------------
class AgentState(TypedDict):
    query: str
    route: Optional[str]
    rag_output: Optional[dict]
    reasoning: Optional[str]
    final_answer: Optional[str]
    steps: List[str]


# ---------------- NODES ----------------

async def router_node(state: AgentState):
    route = route_query(state["query"])
    state["route"] = route
    state["steps"].append(f"router:{route}")
    return state


async def retrieval_node(state: AgentState):
    docs = await run_rag(state["query"])
    state["rag_output"] = docs
    state["steps"].append("retrieval")
    return state


async def tool_node(state: AgentState):

    from app.ai.tools.tool_registry import get_tool

    query = state.get("query", "")

    if any(op in query for op in ["+", "-", "*", "/"]):

        tool = get_tool("calculator")

        if tool:
            result = tool(query)

            state["final_answer"] = result
            state["steps"].append("tool")

            return state

    # fallback if no tool used
    state["steps"].append("tool")
    return state


async def reasoning_node(state: AgentState):

    rag_output = state.get("rag_output", {})

    answer = rag_output.get("answer")

    evidence = {
        "query": state.get("query"),
        "answer": answer,
        "verification": {}
    }

    decision = await run_decision_reasoning(evidence)

    final_answer = getattr(decision, "final_answer", None)

    # 🔥 STRONG FALLBACK
    if not final_answer:
        if answer:
            final_answer = answer
        else:
            final_answer = "I couldn't find a reliable answer."

    state["reasoning"] = final_answer
    state["steps"].append("reasoning")

    return state

async def response_node(state: AgentState):

    # ✅ Priority 1: tool output
    if state.get("final_answer"):
        pass

    # ✅ Priority 2: reasoning
    elif state.get("reasoning"):
        state["final_answer"] = state["reasoning"]

    # ✅ fallback
    else:
        state["final_answer"] = "Hello! How can I help you?"

    state["steps"].append("response")
    return state


# ---------------- CONDITIONAL ROUTING ----------------

def route_decision(state: AgentState):
    route = state.get("route")

    if route == "tool":
        return "tool"

    if route == "retrieval":
        return "retrieval"

    return "response"


# ---------------- GRAPH ----------------

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("tool", tool_node)
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("response", response_node)

    graph.set_entry_point("router")

    # 🔥 dynamic routing
    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "tool": "tool",
            "retrieval": "retrieval",
            "response": "response"
        }
    )

    graph.add_edge("tool", "response")
    graph.add_edge("retrieval", "reasoning")
    graph.add_edge("reasoning", "response")
    graph.add_edge("response", END)

    return graph.compile()


# ---------------- RUNNER ----------------

async def run_agent_graph(query: str):
    graph = build_graph()

    result = await graph.ainvoke({
        "query": query,
        "steps": []
    })

    return result