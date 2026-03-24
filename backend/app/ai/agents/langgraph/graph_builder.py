from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
import re

# existing logic
from app.ai.retrieval.rag_chain import run_rag
from app.ai.reasoning.reasoning_orchestrator import run_decision_reasoning

# reuse your old agent logic
from app.ai.agents.router_agent import route_query
from app.ai.agents.tool_agent import tool_agent

from app.ai.guardrails.input_guard import input_guard
from app.ai.guardrails.prompt_injection import detect_prompt_injection
from app.ai.guardrails.output_guard import output_guard

from app.ai.self_healing.self_healing import self_heal_rag
from app.ai.evaluation.confidence import calculate_confidence
from app.ai.observability.tracer_adv import start_trace, log_step, end_trace

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
    rag_result = await run_rag(state["query"])

    # 🔥 self-healing BEFORE reasoning
    rag_result = await self_heal_rag(
        state["query"],
        rag_result,
        run_rag
    )

    state["rag_output"] = rag_result
    state["steps"].append("retrieval")
    return state


async def tool_node(state: AgentState):

    from app.ai.tools.tool_registry import get_tool

    query = state.get("query", "")

    if re.fullmatch(r"[0-9+\-*/(). ]+", query.strip()):

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

    rag_output = state.get("rag_output") or {}

    answer = rag_output.get("answer")
    verification = rag_output.get("verification", {})

    evidence = {
        "query": state.get("query"),
        "answer": answer,
        "verification": verification,
        "confidence": rag_output.get("confidence"),
        "sources": rag_output.get("sources")
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
        state["final_answer"] = state["final_answer"]

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

    trace = start_trace()

    # 🔥 Input Guard
    guard = input_guard(query)
    if guard["blocked"]:
        return {
            "trace": trace,
            "final_answer": guard["reason"]
        }

    # 🔥 Prompt Injection
    if detect_prompt_injection(query):
        return {
            "trace": trace,
            "final_answer": "Prompt injection detected."
        }

    # 🔥 Run Graph
    graph = build_graph()

    result = await graph.ainvoke({
        "query": query,
        "steps": []
    })

    log_step(trace, "graph_executed")


    # 🔥 Confidence Score
    rag_output = result.get("rag_output") or {}
    confidence_score = rag_output.get("confidence", 0.5)

    # 🔥 Output Guard
    final_answer = output_guard(result.get("final_answer"))

    trace = end_trace(trace)

    return {
        "trace_id": trace["trace_id"],
        "answer": final_answer,
        "confidence_score": confidence_score,
        "steps": result.get("steps"),
        "latency": trace["latency"]
    }
    
    