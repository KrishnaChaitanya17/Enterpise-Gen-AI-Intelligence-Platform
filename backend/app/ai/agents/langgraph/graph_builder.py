from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

# Core systems
from app.ai.retrieval.rag_chain import run_rag
from app.ai.reasoning.reasoning_orchestrator import run_decision_reasoning
from app.ai.tools.tool_registry import get_tool

# Agents
from app.ai.agents.planner_agent import plan_task
from app.ai.agents.router_agent import route_query_llm

# Guards
from app.ai.guardrails.input_guard import input_guard
from app.ai.guardrails.prompt_injection import detect_prompt_injection
from app.ai.guardrails.output_guard import output_guard

# Self-healing
from app.ai.self_healing.self_healing import self_heal_rag

# Observability
from app.ai.observability.tracer_adv import start_trace, log_step, end_trace


# ---------------- STATE ----------------

class AgentState(TypedDict):
    query: str
    plan: Optional[str]
    route: Optional[str]
    rag_output: Optional[dict]
    tool_output: Optional[str]
    reasoning: Optional[str]
    final_answer: Optional[str]
    retries: int
    steps: List[str]


# ---------------- NODES ----------------

async def planner_node(state: AgentState):
    plan = await plan_task(state["query"])
    state["plan"] = plan
    state["steps"].append(f"plan:{plan}")
    return state


async def router_node(state: AgentState):
    route = await route_query_llm(state["query"], state.get("plan"))
    state["route"] = route
    state["steps"].append(f"router:{route}")
    return state


async def retrieval_node(state: AgentState):
    rag_result = await run_rag(state["query"])

    rag_result = await self_heal_rag(
        state["query"],
        rag_result,
        run_rag
    )

    state["rag_output"] = rag_result
    state["steps"].append("retrieval")
    return state


async def tool_node(state: AgentState):
    query = state.get("query", "")

    # 🔥 dynamic tool selection (LLM-style fallback)
    tool = get_tool("calculator")

    if tool and any(op in query for op in ["+", "-", "*", "/"]):
        result = tool(query)
        state["tool_output"] = result

    state["steps"].append("tool")
    return state


async def reasoning_node(state: AgentState):

    rag_output = state.get("rag_output") or {}
    tool_output = state.get("tool_output")

    answer = tool_output or rag_output.get("answer")

    evidence = {
        "query": state.get("query"),
        "answer": answer,
        "verification": rag_output.get("verification", {}),
        "confidence": rag_output.get("confidence"),
        "sources": rag_output.get("sources")
    }

    decision = await run_decision_reasoning(evidence)

    final_answer = getattr(decision, "final_answer", None)

    if not final_answer:
        final_answer = answer or "I couldn't find a reliable answer."

    state["reasoning"] = final_answer
    state["steps"].append("reasoning")

    return state


async def retry_node(state: AgentState):
    state["retries"] += 1
    state["steps"].append("retry")
    return state


async def response_node(state: AgentState):

    if state.get("reasoning"):
        state["final_answer"] = state["reasoning"]
    elif state.get("tool_output"):
        state["final_answer"] = state["tool_output"]
    else:
        state["final_answer"] = "I couldn't generate a proper answer."

    state["steps"].append("response")
    return state


# ---------------- DECISION LOGIC ----------------

def route_decision(state: AgentState):
    route = state.get("route")

    if route == "tool":
        return "tool"

    if route == "retrieval":
        return "retrieval"

    return "response"


def retry_decision(state: AgentState):
    retries = state.get("retries", 0)
    answer = state.get("reasoning", "")

    if retries < 1 and (not answer or len(answer) < 20):
        return "retry"

    return "response"


# ---------------- GRAPH ----------------

def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("planner", planner_node)
    graph.add_node("router", router_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("tool", tool_node)
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("retry", retry_node)
    graph.add_node("response", response_node)

    # Entry
    graph.set_entry_point("planner")

    # Flow
    graph.add_edge("planner", "router")

    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "tool": "tool",
            "retrieval": "retrieval",
            "response": "response"
        }
    )

    graph.add_edge("tool", "reasoning")
    graph.add_edge("retrieval", "reasoning")

    graph.add_conditional_edges(
        "reasoning",
        retry_decision,
        {
            "retry": "retry",
            "response": "response"
        }
    )

    graph.add_edge("retry", "retrieval")
    graph.add_edge("response", END)

    return graph.compile()


# ---------------- RUNNER ----------------

async def run_agent_graph(query: str):

    trace = start_trace()

    # Guards
    guard = input_guard(query)
    if guard["blocked"]:
        return {"answer": guard["reason"]}

    if detect_prompt_injection(query):
        return {"answer": "Prompt injection detected."}

    graph = build_graph()

    result = await graph.ainvoke({
        "query": query,
        "steps": [],
        "retries": 0
    })

    log_step(trace, "graph_executed")

    final_answer = output_guard(result.get("final_answer"))

    trace = end_trace(trace)

    return {
        "trace_id": trace["trace_id"],
        "answer": final_answer,
        "steps": result.get("steps"),
        "latency": trace["latency"]
    }