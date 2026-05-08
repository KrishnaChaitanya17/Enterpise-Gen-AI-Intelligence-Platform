from typing import TypedDict, List, Optional
from app.ai.evaluation.confidence import calculate_confidence
from langgraph.graph import StateGraph, END
import re

# Core systems
from app.ai.retrieval.rag_chain import run_rag
from app.ai.reasoning.reasoning_orchestrator import run_decision_reasoning
from app.ai.tools.tool_registry import get_tool, select_tool

# Agents
from app.ai.agents.planner_agent import plan_task
from app.ai.agents.router_agent import route_query_llm

# Guards
from app.ai.guardrails.input_guard import input_guard
from app.ai.guardrails.prompt_injection import detect_prompt_injection
from app.ai.guardrails.output_guard import output_guard
from app.ai.guardrails.policy_engine import evaluate_policy
from app.ai.guardrails.hallucination_guard import hallucination_guard

# Self-healing
from app.ai.self_healing.self_healing import self_heal_rag

# Observability
from app.ai.observability.tracer_adv import start_trace, log_step, end_trace
from app.ai.observability.trace_store import save_trace

from app.ai.memory.conversation_memory import get_conversation


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
    memory: Optional[str]


# ---------------- NODES ----------------

async def planner_node(state: AgentState):
    history = get_conversation("default")

    context = "\n".join(
        [f"{m['query']} -> {m['answer']}" for m in history[-3:]]
    ) if history else ""

    plan = await plan_task(
        f"Context:\n{context}\n\nTask:\n{state['query']}"
    )

    state["plan"] = plan
    state["memory"] = context
    state["steps"].append(f"plan:{plan}")

    return state


async def router_node(state: AgentState):
    query = state["query"].lower()

    is_math = bool(re.search(r"\d+\s*[\+\-\*/]\s*\d+", query))

    if is_math:
        if any(word in query for word in ["explain", "what", "define"]):
            route = "hybrid"
        else:
            route = "tool"
    else:
        route = await route_query_llm(query, state.get("plan"))

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

    state["rag_output"] = rag_result or {}
    state["steps"].append("retrieval")
    return state


async def tool_node(state: AgentState):
    query = state.get("query", "")

    tool_name = await select_tool(query)

    if tool_name:
        tool = get_tool(tool_name)

        if tool:
            result = tool(query)
            state["tool_output"] = str(result)
            state["steps"].append(f"tool:{tool_name}")
            return state

    state["tool_output"] = None
    state["steps"].append("tool:none")
    return state


async def reasoning_node(state: AgentState):

    route = state.get("route")

    # 🔥 1. HYBRID: combine RAG + tool
    if route == "hybrid":
        tool_output = None

        tool_name = await select_tool(state["query"])
        if tool_name:
            tool = get_tool(tool_name)
            if tool:
                try:
                    tool_output = str(tool(state["query"]))
                except Exception:
                    tool_output = None

        rag_output = state.get("rag_output") or {}
        answer = rag_output.get("answer", "")

        combined = answer

        if tool_output:
            combined = f"{answer}\n\nCalculation Result: {tool_output}"

        state["reasoning"] = combined
        state["steps"].append("reasoning:hybrid")

        return state

    # 🔥 2. TOOL ONLY (fast path)
    if state.get("tool_output"):
        state["reasoning"] = state["tool_output"]
        state["steps"].append("reasoning:tool_direct")
        return state

    # 🔥 3. RAG + reasoning agents
    rag_output = state.get("rag_output") or {}
    memory = state.get("memory")

    answer = rag_output.get("answer")

    confidence = calculate_confidence(rag_output)

    evidence = {
        "query": state.get("query"),
        "answer": answer,
        "memory": memory,
        "verification": rag_output.get("verification", {}),
        "confidence": confidence,
        "sources": rag_output.get("sources")
    }

    decision = await run_decision_reasoning(evidence)

    final_answer = getattr(decision, "final_answer", None)

    if not final_answer:
        final_answer = answer or "I couldn't find a reliable answer."

    # ✅ attach confidence back
    rag_output["confidence"] = confidence
    state["rag_output"] = rag_output

    state["reasoning"] = final_answer
    state["steps"].append("reasoning")

    return state


async def retry_node(state: AgentState):
    state["retries"] += 1
    state["steps"].append("retry")
    return state


async def response_node(state: AgentState):

    answer = (
        state.get("reasoning") or
        state.get("tool_output") or
        "I couldn't generate a proper answer."
    )

    query = state.get("query", "").lower()

    # ✅ Always allow safe educational queries
    SAFE_QUERIES = ["what is", "explain", "define"]

    if any(q in query for q in SAFE_QUERIES) and state.get("reasoning"):
        state["final_answer"] = answer
        state["steps"].append("response:safe_query")
        return state

    # ✅ Tool output → always trust
    if state.get("tool_output") and not state.get("rag_output"):
        state["final_answer"] = answer
        state["steps"].append("response:tool")
        return state

    rag = state.get("rag_output", {})
    confidence = rag.get("confidence", 0.5)

    # ✅ Trust high confidence
    if confidence >= 0.6:
        state["final_answer"] = answer
        state["steps"].append("response:trusted")
        return state

    # 🔍 Only check hallucination when low confidence
    is_safe = await hallucination_guard(
        state["query"],
        answer,
        rag.get("sources", [])
    )

    # ❌ Only block when BOTH bad
    if not is_safe and confidence < 0.4:
        state["final_answer"] = "Blocked: Low confidence & hallucination risk"
        state["steps"].append("response:blocked")
        return state
    
    decision = evaluate_policy({
        "hallucination": not is_safe,
        "confidence": confidence
    })

    if not decision["allow"] and confidence < 0.4:
        state["final_answer"] = f"Blocked: {decision['reason']}"
        return state

    # ✅ Otherwise allow
    final_answer, _ = output_guard(answer)
    state["final_answer"] = final_answer
    state["steps"].append("response:allowed")

    return state


# ---------------- DECISIONS ----------------

def route_decision(state: AgentState):
    route = state.get("route")

    if route == "tool":
        return "tool"

    if route == "retrieval":
        return "retrieval"

    if route == "hybrid":
        return "retrieval"   # 🔥 go to retrieval first

    return "response"


def retry_decision(state: AgentState):
    retries = state.get("retries", 0)
    answer = state.get("reasoning", "")
    rag = state.get("rag_output", {})

    confidence = rag.get("confidence", 0.5)

    # 🔥 If tool already answered → skip retry
    if state.get("tool_output"):
        return "response"

    if retries < 1 and (
        not answer or
        confidence < 0.4
    ):
        return "retry"

    return "response"


# ---------------- GRAPH ----------------

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("router", router_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("tool", tool_node)
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("retry", retry_node)
    graph.add_node("response", response_node)

    graph.set_entry_point("planner")

    # Linear flow
    graph.add_edge("planner", "router")

    # Route decision
    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "tool": "tool",
            "retrieval": "retrieval",
            "response": "response",
            "hybrid": "retrieval"  # handled as retrieval-first
        }
    )

    # ✅ NO PARALLEL PATHS
    graph.add_edge("tool", "reasoning")
    graph.add_edge("retrieval", "reasoning")

    # Retry logic
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

    clean_query = query.strip()

    result = await graph.ainvoke({
        "query": clean_query,
        "steps": [],
        "retries": 0
    })

    log_step(trace, "graph_executed")

    raw_answer = (
        result.get("final_answer") or
        result.get("reasoning") or
        result.get("tool_output") or
        "No response generated."
    )

    if raw_answer.startswith("Blocked") and result.get("reasoning"):
        raw_answer = result["reasoning"]

    # 🔥 Apply output guard at final stage (global safety layer)
    final_answer, _ = output_guard(raw_answer)

    result = {**result, "final_answer": final_answer}

    trace = end_trace(trace)

    # 🔥 SAVE TRACE (FIXED)
    save_trace({
        "trace_id": trace["trace_id"],
        "query": query,
        "answer": final_answer,
        "latency": trace["latency"],
        "steps": result.get("steps", []),
        "status": trace.get("status","success"),
        "error": None,
        "enterprise": {},
        "moderation": {},
        "timestamp": trace.get("end_time")
    })

    print("FINAL ANSWER DEBUG:", final_answer)
    print("RESULT FINAL:", result.get("final_answer"))

    return {
        "trace_id": trace["trace_id"],
        "answer": final_answer,  # ✅ always correct
        "steps": result.get("steps", []),
        "latency": trace["latency"]
    }